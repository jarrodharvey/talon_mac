"""
Advanced Talon Command Troubleshooting Agent

This module provides comprehensive automated testing capabilities for newly developed Talon commands.
It can switch windows, capture screenshots, execute commands via REPL, analyze results,
and provide detailed recommendations for fixing issues.

Features:
- REPL Integration: Execute Talon commands via ~/.talon/bin/repl
- Window Management: Switch between applications using community focus extension
- Screenshot Analysis: Capture and analyze before/after screenshots
- Log Analysis: Monitor and interpret Talon logs for errors and debugging info
- Real-world Testing: Test commands in target applications "in the field"
- Test Reporting: Comprehensive analysis with actionable recommendations
"""

import subprocess
import time
import os
import tempfile
import json
import re
from datetime import datetime
from talon import actions, ui, screen, settings, registry
import sys
from pathlib import Path

class TalonTroubleshooter:
    def __init__(self):
        self.original_window = None
        self.screenshot_dir = "/Users/jarrod/.talon/user/jarrod/claude_helpers/screenshots"
        self.test_session_id = None
        self.current_test_data = {}
        self.error_patterns = [
            r'ERROR.*',
            r'Exception.*',
            r'Traceback.*',
            r'AttributeError.*',
            r'ImportError.*',
            r'NameError.*',
            r'TypeError.*',
            r'ValueError.*',
            r'RuntimeError.*',
            r'talon\..*error.*',
            r'Failed.*',
            r'Could not.*',
            r'Unable to.*'
        ]
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
    def start_test_session(self, test_name=""):
        """Start a new test session with unique ID"""
        self.test_session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{test_name}"
        self.current_test_data = {
            'session_id': self.test_session_id,
            'test_name': test_name,
            'start_time': datetime.now().isoformat(),
            'screenshots': [],
            'commands_executed': [],
            'errors_found': [],
            'recommendations': []
        }
        print(f"Started test session: {self.test_session_id}")
        
    def end_test_session(self):
        """End current test session and save data"""
        if self.current_test_data:
            self.current_test_data['end_time'] = datetime.now().isoformat()
            # Save session data
            session_file = os.path.join(self.screenshot_dir, f"session_{self.test_session_id}.json")
            with open(session_file, 'w') as f:
                json.dump(self.current_test_data, f, indent=2)
            print(f"Test session saved: {session_file}")
        self.test_session_id = None
        self.current_test_data = {}
        
    def capture_screenshot(self, filename_suffix="", description=""):
        """Capture a screenshot for analysis with metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_prefix = f"{self.test_session_id}_" if self.test_session_id else ""
        filename = f"{session_prefix}troubleshoot_{timestamp}{filename_suffix}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        try:
            # Capture screenshot using Talon's screen capture
            screenshot = screen.capture()
            screenshot.save(filepath)
            
            # Add to session data if session is active
            if self.test_session_id:
                screenshot_data = {
                    'filepath': filepath,
                    'timestamp': timestamp,
                    'description': description,
                    'suffix': filename_suffix
                }
                self.current_test_data['screenshots'].append(screenshot_data)
            
            print(f"Screenshot captured: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            return None
    
    def focus_application(self, app_name):
        """Focus a specific application window using community focus extension"""
        try:
            # Store current window for later restoration
            self.original_window = ui.active_window()
            original_app = self.original_window.app.name if self.original_window else "unknown"
            
            print(f"Switching from {original_app} to {app_name}...")
            
            # Use community focus command
            actions.user.switcher_focus(app_name)
            time.sleep(1.5)  # Allow time for window switch
            
            # Verify the switch was successful
            current_window = ui.active_window()
            current_app = current_window.app.name if current_window else "unknown"
            
            success = current_app.lower() == app_name.lower()
            
            # Capture verification screenshot
            screenshot_path = self.capture_screenshot(
                f"_focus_{app_name}", 
                f"After focusing {app_name} (success: {success})"
            )
            
            if not success:
                error_msg = f"Failed to focus {app_name}. Current app: {current_app}"
                print(error_msg)
                if self.test_session_id:
                    self.current_test_data['errors_found'].append({
                        'type': 'focus_failure',
                        'message': error_msg,
                        'expected_app': app_name,
                        'actual_app': current_app
                    })
                    
            return screenshot_path
            
        except Exception as e:
            error_msg = f"Error focusing {app_name}: {e}"
            print(error_msg)
            if self.test_session_id:
                self.current_test_data['errors_found'].append({
                    'type': 'focus_exception',
                    'message': error_msg,
                    'app_name': app_name
                })
            return None
    
    def return_to_terminal(self):
        """Return focus to the original terminal window"""
        try:
            if self.original_window:
                self.original_window.focus()
            else:
                # Fallback: focus terminal/iTerm
                actions.user.switcher_focus("terminal")
            time.sleep(0.5)
            
            screenshot_path = self.capture_screenshot("_back_to_terminal")
            return screenshot_path
            
        except Exception as e:
            print(f"Error returning to terminal: {e}")
            return None
    
    def execute_repl_command(self, command, timeout=15, description=""):
        """Execute a command via Talon REPL and capture detailed output"""
        print(f"Executing REPL command: {command}")
        
        try:
            # Use echo to pipe command to Talon REPL
            repl_command = f'echo \'{command}\' | ~/.talon/bin/repl'
            start_time = time.time()
            
            result = subprocess.run(
                repl_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            command_result = {
                'command': command,
                'description': description,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'execution_time': execution_time,
                'timeout': timeout,
                'success': result.returncode == 0 and not result.stderr.strip()
            }
            
            # Add to session data if session is active
            if self.test_session_id:
                self.current_test_data['commands_executed'].append(command_result)
                
                # Check for errors in output
                if result.stderr.strip():
                    self.current_test_data['errors_found'].append({
                        'type': 'repl_stderr',
                        'command': command,
                        'message': result.stderr.strip()
                    })
                
                if result.returncode != 0:
                    self.current_test_data['errors_found'].append({
                        'type': 'repl_nonzero_exit',
                        'command': command,
                        'returncode': result.returncode
                    })
            
            return command_result
            
        except subprocess.TimeoutExpired:
            error_result = {
                'command': command,
                'description': description,
                'error': f'REPL command timed out after {timeout} seconds',
                'success': False
            }
            if self.test_session_id:
                self.current_test_data['errors_found'].append({
                    'type': 'repl_timeout',
                    'command': command,
                    'timeout': timeout
                })
            return error_result
            
        except Exception as e:
            error_result = {
                'command': command,
                'description': description,
                'error': f'REPL execution failed: {e}',
                'success': False
            }
            if self.test_session_id:
                self.current_test_data['errors_found'].append({
                    'type': 'repl_exception',
                    'command': command,
                    'exception': str(e)
                })
            return error_result
    
    def check_talon_logs(self, lines=30, analyze_errors=True):
        """Check recent Talon logs for errors or relevant messages with analysis"""
        try:
            log_path = "/Users/jarrod/.talon/talon.log"
            result = subprocess.run(
                f"tail -{lines} {log_path}",
                shell=True,
                capture_output=True,
                text=True
            )
            
            log_content = result.stdout
            
            if analyze_errors:
                error_analysis = self.analyze_log_errors(log_content)
                return {
                    'raw_logs': log_content,
                    'error_analysis': error_analysis,
                    'lines_checked': lines
                }
            
            return log_content
            
        except Exception as e:
            return f"Error reading logs: {e}"
    
    def analyze_log_errors(self, log_content):
        """Analyze log content for errors and patterns"""
        lines = log_content.split('\n')
        errors_found = []
        patterns_matched = []
        
        for i, line in enumerate(lines):
            # Check for error patterns
            for pattern in self.error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    error_info = {
                        'line_number': i + 1,
                        'line_content': line.strip(),
                        'pattern': pattern,
                        'context': self._get_log_context(lines, i)
                    }
                    errors_found.append(error_info)
                    if pattern not in patterns_matched:
                        patterns_matched.append(pattern)
        
        # Look for specific gaming/testing related issues
        gaming_issues = self._identify_gaming_issues(log_content)
        
        return {
            'errors_found': errors_found,
            'patterns_matched': patterns_matched,
            'gaming_issues': gaming_issues,
            'total_errors': len(errors_found)
        }
    
    def _get_log_context(self, lines, error_line_index, context_lines=2):
        """Get context around an error line"""
        start = max(0, error_line_index - context_lines)
        end = min(len(lines), error_line_index + context_lines + 1)
        
        context = []
        for i in range(start, end):
            prefix = ">>> " if i == error_line_index else "    "
            context.append(f"{prefix}{lines[i].strip()}")
        
        return '\n'.join(context)
    
    def _identify_gaming_issues(self, log_content):
        """Identify gaming-specific issues in logs"""
        gaming_patterns = [
            (r'image.*not found', 'Image template matching failed'),
            (r'cubes.*error', 'Cubes system error'),
            (r'mouse.*helper.*error', 'Mouse helper system error'),
            (r'gaze.*ocr.*error', 'OCR system error'),
            (r'switcher.*focus.*error', 'Window focus error'),
            (r'template.*match.*failed', 'Template matching failed'),
            (r'coordinate.*invalid', 'Invalid coordinate error'),
            (r'navigation.*failed', 'Navigation system error')
        ]
        
        issues = []
        for pattern, description in gaming_patterns:
            if re.search(pattern, log_content, re.IGNORECASE):
                issues.append({
                    'pattern': pattern,
                    'description': description,
                    'severity': self._assess_issue_severity(pattern)
                })
        
        return issues
    
    def _assess_issue_severity(self, pattern):
        """Assess the severity of an issue based on pattern"""
        high_severity = ['error', 'exception', 'failed', 'invalid']
        medium_severity = ['warning', 'timeout', 'retry']
        
        pattern_lower = pattern.lower()
        
        if any(keyword in pattern_lower for keyword in high_severity):
            return 'high'
        elif any(keyword in pattern_lower for keyword in medium_severity):
            return 'medium'
        else:
            return 'low'
    
    def comprehensive_command_test(self, app_name, commands, test_name=""):
        """
        Execute a comprehensive test suite for multiple related commands
        
        Args:
            app_name: Target application for testing
            commands: List of command dictionaries with 'command', 'description', 'expected_result' 
            test_name: Human-readable test name
        """
        self.start_test_session(test_name or f"test_{app_name}")
        
        try:
            # Initial setup
            print(f"=== Starting Comprehensive Test: {test_name} ===")
            
            # 1. Capture baseline state
            baseline_screenshot = self.capture_screenshot("_baseline", "Initial state before test")
            
            # 2. Focus target application
            print(f"Focusing target application: {app_name}")
            focus_screenshot = self.focus_application(app_name)
            
            # 3. Execute each command with analysis
            for i, cmd_info in enumerate(commands):
                command = cmd_info['command']
                description = cmd_info.get('description', '')
                expected = cmd_info.get('expected_result', 'success')
                
                print(f"\n--- Test Step {i+1}: {description} ---")
                
                # Capture before screenshot
                before_screenshot = self.capture_screenshot(
                    f"_step{i+1}_before", 
                    f"Before: {description}"
                )
                
                # Execute command
                result = self.execute_repl_command(command, description=description)
                
                # Wait for command effects
                time.sleep(1.5)
                
                # Capture after screenshot
                after_screenshot = self.capture_screenshot(
                    f"_step{i+1}_after", 
                    f"After: {description}"
                )
                
                # Analyze results vs expectations
                self._analyze_command_result(result, expected, description)
            
            # 4. Final log analysis
            print("\n--- Final Analysis ---")
            log_analysis = self.check_talon_logs(50, analyze_errors=True)
            
            # 5. Generate recommendations
            recommendations = self._generate_recommendations()
            self.current_test_data['recommendations'] = recommendations
            
            # 6. Return to terminal
            terminal_screenshot = self.return_to_terminal()
            
            # 7. End session and generate report
            self.end_test_session()
            
            return self._generate_comprehensive_report()
            
        except Exception as e:
            error_msg = f"Comprehensive test failed: {e}"
            print(error_msg)
            self.current_test_data['errors_found'].append({
                'type': 'test_framework_error',
                'message': error_msg
            })
            self.return_to_terminal()
            self.end_test_session()
            return self._generate_comprehensive_report()
    
    def _analyze_command_result(self, result, expected_result, description):
        """Analyze command execution result against expectations"""
        analysis = {
            'command': result.get('command', 'unknown'),
            'description': description,
            'expected': expected_result,
            'actual_success': result.get('success', False),
            'execution_time': result.get('execution_time', 0),
            'issues': []
        }
        
        # Check if result matches expectation
        if expected_result == 'success' and not result.get('success', False):
            analysis['issues'].append('Command failed when success was expected')
        elif expected_result == 'failure' and result.get('success', False):
            analysis['issues'].append('Command succeeded when failure was expected')
        
        # Check execution time (flag slow commands)
        if result.get('execution_time', 0) > 5:
            analysis['issues'].append(f"Slow execution time: {result['execution_time']:.2f}s")
        
        # Check for specific error patterns
        if 'stderr' in result and result['stderr']:
            analysis['issues'].append(f"STDERR output: {result['stderr']}")
        
        if analysis['issues']:
            self.current_test_data['errors_found'].append({
                'type': 'command_analysis',
                'analysis': analysis
            })
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on test results"""
        recommendations = []
        errors = self.current_test_data.get('errors_found', [])
        
        # Analyze error patterns and generate specific recommendations
        error_types = [error.get('type', 'unknown') for error in errors]
        
        if 'focus_failure' in error_types:
            recommendations.append({
                'category': 'Window Management',
                'issue': 'Application focus failed',
                'recommendation': 'Check if target application is running and accessible. Verify app name spelling.',
                'priority': 'high'
            })
        
        if 'repl_timeout' in error_types:
            recommendations.append({
                'category': 'Command Execution',
                'issue': 'REPL commands timing out',
                'recommendation': 'Commands may be hanging. Check for infinite loops or blocking operations.',
                'priority': 'high'
            })
        
        if 'template_match_failed' in error_types:
            recommendations.append({
                'category': 'Image Recognition',
                'issue': 'Template matching failed',
                'recommendation': 'Verify image files exist and are current. Consider updating template images.',
                'priority': 'medium'
            })
        
        # Check for gaming-specific issues
        gaming_errors = [e for e in errors if 'gaming' in str(e).lower() or 'cubes' in str(e).lower()]
        if gaming_errors:
            recommendations.append({
                'category': 'Gaming Systems',
                'issue': 'Gaming-related functionality issues',
                'recommendation': 'Check gaming helper modules and image template paths. Verify OCR system is working.',
                'priority': 'medium'
            })
        
        # Performance recommendations
        slow_commands = [e for e in errors if 'Slow execution' in str(e)]
        if slow_commands:
            recommendations.append({
                'category': 'Performance',
                'issue': 'Slow command execution detected',
                'recommendation': 'Optimize command implementations and reduce unnecessary delays.',
                'priority': 'low'
            })
        
        # General recommendations based on error count
        if len(errors) == 0:
            recommendations.append({
                'category': 'Success',
                'issue': 'No errors detected',
                'recommendation': 'All tests passed successfully. Commands appear to be working correctly.',
                'priority': 'info'
            })
        elif len(errors) > 5:
            recommendations.append({
                'category': 'System Health',
                'issue': 'Multiple errors detected',
                'recommendation': 'Consider systematic debugging. Check Talon configuration and restart if needed.',
                'priority': 'high'
            })
        
        return recommendations
    
    def test_arbitrary_command(self, app_name, command, command_description=""):
        """
        Test any arbitrary Talon command in a specific application
        
        Args:
            app_name: Application to focus for testing
            command: Talon command to execute via REPL
            command_description: Human-readable description of what the command does
        """
        results = {
            'app_name': app_name,
            'command': command,
            'description': command_description,
            'screenshots': [],
            'repl_outputs': [],
            'logs': [],
            'errors': []
        }
        
        try:
            # 1. Focus target application
            print(f"Focusing {app_name}...")
            screenshot = self.focus_application(app_name)
            if screenshot:
                results['screenshots'].append(('before_command', screenshot))
            
            # 2. Execute the command
            print(f"Executing command: {command}")
            repl_result = self.execute_repl_command(command)
            results['repl_outputs'].append(('command_execution', repl_result))
            
            # 3. Wait and capture result
            time.sleep(1)
            screenshot = self.capture_screenshot("_after_command")
            results['screenshots'].append(('after_command', screenshot))
            
            # 4. Check logs
            logs = self.check_talon_logs(20)
            results['logs'].append(('command_logs', logs))
            
            # 5. Return to terminal
            screenshot = self.return_to_terminal()
            if screenshot:
                results['screenshots'].append(('back_to_terminal', screenshot))
                
        except Exception as e:
            results['errors'].append(f"Command test error: {e}")
            self.return_to_terminal()
        
        return results
    
    def _generate_comprehensive_report(self):
        """Generate comprehensive test report with recommendations"""
        if not self.current_test_data:
            return "No test data available. Run a test session first."
        
        report = []
        data = self.current_test_data
        
        # Header
        report.append("=" * 60)
        report.append("TALON TROUBLESHOOTING AGENT - COMPREHENSIVE REPORT")
        report.append("=" * 60)
        report.append(f"Test Session: {data.get('session_id', 'unknown')}")
        report.append(f"Test Name: {data.get('test_name', 'Unnamed Test')}")
        report.append(f"Start Time: {data.get('start_time', 'unknown')}")
        report.append(f"End Time: {data.get('end_time', 'unknown')}")
        report.append("")
        
        # Executive Summary
        total_commands = len(data.get('commands_executed', []))
        total_errors = len(data.get('errors_found', []))
        total_screenshots = len(data.get('screenshots', []))
        
        report.append("EXECUTIVE SUMMARY:")
        report.append(f"  Commands Executed: {total_commands}")
        report.append(f"  Errors Found: {total_errors}")
        report.append(f"  Screenshots Captured: {total_screenshots}")
        
        if total_errors == 0:
            report.append("  Status: ✅ ALL TESTS PASSED")
        elif total_errors <= 2:
            report.append("  Status: ⚠️  MINOR ISSUES DETECTED")
        else:
            report.append("  Status: ❌ SIGNIFICANT ISSUES DETECTED")
        report.append("")
        
        # Command Execution Results
        if data.get('commands_executed'):
            report.append("COMMAND EXECUTION RESULTS:")
            for i, cmd in enumerate(data['commands_executed'], 1):
                status = "✅ SUCCESS" if cmd.get('success', False) else "❌ FAILED"
                report.append(f"  {i}. {status} - {cmd.get('description', cmd.get('command', 'Unknown'))}")
                report.append(f"     Command: {cmd.get('command', 'N/A')}")
                report.append(f"     Execution Time: {cmd.get('execution_time', 0):.2f}s")
                if not cmd.get('success', False):
                    report.append(f"     Error: {cmd.get('error', 'Unknown error')}")
                report.append("")
        
        # Error Analysis
        if data.get('errors_found'):
            report.append("ERROR ANALYSIS:")
            error_categories = {}
            for error in data['errors_found']:
                error_type = error.get('type', 'unknown')
                if error_type not in error_categories:
                    error_categories[error_type] = []
                error_categories[error_type].append(error)
            
            for category, errors in error_categories.items():
                report.append(f"  {category.upper().replace('_', ' ')} ({len(errors)} errors):")
                for error in errors:
                    report.append(f"    - {error.get('message', str(error))}")
                report.append("")
        
        # Screenshots
        if data.get('screenshots'):
            report.append("SCREENSHOTS CAPTURED:")
            for screenshot in data['screenshots']:
                report.append(f"  {screenshot['description']}")
                report.append(f"    File: {screenshot['filepath']}")
                report.append(f"    Time: {screenshot['timestamp']}")
                report.append("")
        
        # Recommendations
        if data.get('recommendations'):
            report.append("ACTIONABLE RECOMMENDATIONS:")
            high_priority = [r for r in data['recommendations'] if r.get('priority') == 'high']
            medium_priority = [r for r in data['recommendations'] if r.get('priority') == 'medium']
            low_priority = [r for r in data['recommendations'] if r.get('priority') == 'low']
            info_items = [r for r in data['recommendations'] if r.get('priority') == 'info']
            
            for priority, items in [('HIGH PRIORITY', high_priority), ('MEDIUM PRIORITY', medium_priority), ('LOW PRIORITY', low_priority), ('INFO', info_items)]:
                if items:
                    report.append(f"  {priority}:")
                    for rec in items:
                        report.append(f"    📋 {rec['category']}: {rec['issue']}")
                        report.append(f"       💡 {rec['recommendation']}")
                        report.append("")
        
        # Next Steps
        report.append("SUGGESTED NEXT STEPS:")
        if total_errors == 0:
            report.append("  1. ✅ All tests passed - commands are working correctly")
            report.append("  2. 📝 Consider adding more edge case tests")
            report.append("  3. 🔄 Run periodic regression tests")
        else:
            report.append("  1. 🔍 Review error details above")
            report.append("  2. 🛠️  Implement high-priority recommendations")
            report.append("  3. 🧪 Re-run tests after fixes")
            report.append("  4. 📋 Check Talon logs for additional context")
        
        report.append("")
        report.append("=" * 60)
        
        return '\n'.join(report)
    
    def test_cubes_functionality(self, target_name=None):
        """Enhanced cubes functionality test with comprehensive analysis"""
        commands = [
            {
                'command': 'actions.user.show_cubes()',
                'description': 'Show cubes overlay',
                'expected_result': 'success'
            }
        ]
        
        if target_name:
            commands.append({
                'command': f'actions.user.navigate_to_cube("{target_name}")',
                'description': f'Navigate to cube: {target_name}',
                'expected_result': 'success'
            })
        
        return self.comprehensive_command_test("moonlight", commands, f"cubes_test_{target_name or 'basic'}")

# Global instance for easy access
troubleshooter = TalonTroubleshooter()

# Enhanced convenience functions for the specialized agent

def test_cubes_in_moonlight(target_name=None):
    """Enhanced cubes functionality testing with comprehensive analysis"""
    print(f"🔬 Starting enhanced cubes test{f' for target: {target_name}' if target_name else ''}...")
    report = troubleshooter.test_cubes_functionality(target_name)
    print(report)
    return report

def test_command_in_app(app_name, command, description=""):
    """Test a single command with basic analysis"""
    commands = [{
        'command': command,
        'description': description or f"Test {command}",
        'expected_result': 'success'
    }]
    
    print(f"🔬 Testing command '{command}' in {app_name}...")
    report = troubleshooter.comprehensive_command_test(app_name, commands, f"single_command_{app_name}")
    print(report)
    return report

def test_gaming_workflow(app_name, workflow_commands, workflow_name=""):
    """Test a complete gaming workflow with multiple commands"""
    print(f"🎮 Testing gaming workflow: {workflow_name or 'unnamed'}")
    report = troubleshooter.comprehensive_command_test(app_name, workflow_commands, workflow_name)
    print(report)
    return report

def test_ocr_navigation_workflow(app_name="moonlight"):
    """Test OCR-based navigation workflow"""
    commands = [
        {
            'command': 'actions.user.disconnect_ocr_eye_tracker()',
            'description': 'Disconnect OCR eye tracker for full screen scan',
            'expected_result': 'success'
        },
        {
            'command': 'actions.user.show_ocr_overlay("text")',
            'description': 'Show OCR text overlay',
            'expected_result': 'success'
        },
        {
            'command': 'actions.user.connect_ocr_eye_tracker()',
            'description': 'Reconnect OCR eye tracker',
            'expected_result': 'success'
        }
    ]
    
    return test_gaming_workflow(app_name, commands, "ocr_navigation_test")

def test_image_recognition_workflow(app_name="moonlight", test_images=None):
    """Test image recognition and template matching"""
    if not test_images:
        test_images = ["bg3_search1.png", "apple_logo.png"]
    
    commands = []
    for image in test_images:
        commands.append({
            'command': f'actions.user.click_image("{image}")',
            'description': f'Test image recognition for {image}',
            'expected_result': 'success'
        })
    
    return test_gaming_workflow(app_name, commands, "image_recognition_test")

def test_menu_navigation_workflow(app_name="moonlight"):
    """Test menu navigation with pathfinding"""
    commands = [
        {
            'command': 'actions.user.get_text_coordinates("Help")',
            'description': 'Get coordinates of Help text via OCR',
            'expected_result': 'success'
        },
        {
            'command': 'actions.user.find_template_flexible("chained_echoes_highlight.png")',
            'description': 'Find highlight box template',
            'expected_result': 'success'
        },
        {
            'command': 'actions.user.navigate_to_text_with_highlight_wasd("Help", "chained_echoes_highlight.png")',
            'description': 'Navigate from highlight to Help text using WASD',
            'expected_result': 'success'
        }
    ]
    
    return test_gaming_workflow(app_name, commands, "menu_navigation_test")

def quick_app_focus_test(app_name):
    """Quick test to verify application focus is working"""
    print(f"🎯 Quick focus test for {app_name}...")
    troubleshooter.start_test_session(f"focus_test_{app_name}")
    
    screenshot1 = troubleshooter.capture_screenshot("_before_focus", "Before focus attempt")
    success_screenshot = troubleshooter.focus_application(app_name)
    screenshot2 = troubleshooter.return_to_terminal()
    
    report = troubleshooter._generate_comprehensive_report()
    troubleshooter.end_test_session()
    
    print(report)
    return report

def analyze_recent_logs(lines=50):
    """Analyze recent Talon logs for issues"""
    print("📋 Analyzing recent Talon logs...")
    log_analysis = troubleshooter.check_talon_logs(lines, analyze_errors=True)
    
    if isinstance(log_analysis, dict):
        error_analysis = log_analysis['error_analysis']
        print(f"\n📊 LOG ANALYSIS RESULTS:")
        print(f"Lines analyzed: {log_analysis['lines_checked']}")
        print(f"Errors found: {error_analysis['total_errors']}")
        
        if error_analysis['gaming_issues']:
            print(f"\n🎮 Gaming-specific issues:")
            for issue in error_analysis['gaming_issues']:
                print(f"  - {issue['description']} (severity: {issue['severity']})")
        
        if error_analysis['errors_found']:
            print(f"\n❌ Recent errors:")
            for error in error_analysis['errors_found'][-5:]:  # Last 5 errors
                print(f"  Line {error['line_number']}: {error['line_content']}")
    else:
        print("Raw logs:")
        print(log_analysis)
    
    return log_analysis

def troubleshoot_system_health():
    """Comprehensive system health check"""
    print("🏥 Running comprehensive system health check...")
    
    health_commands = [
        {
            'command': 'print("Talon is responsive")',
            'description': 'Basic Talon responsiveness test',
            'expected_result': 'success'
        },
        {
            'command': 'actions.user.switcher_focus("terminal")',
            'description': 'Test window switching functionality',
            'expected_result': 'success'
        },
        {
            'command': 'actions.sleep(0.1)',
            'description': 'Test Talon actions system',
            'expected_result': 'success'
        }
    ]
    
    report = troubleshooter.comprehensive_command_test("terminal", health_commands, "system_health_check")
    print(report)
    
    # Also analyze logs
    print("\n" + "="*50)
    analyze_recent_logs(30)
    
    return report

def run_comprehensive_cubes_test():
    """Run a comprehensive cubes test with multiple commands"""
    commands = [
        {
            'command': 'actions.user.show_cubes()',
            'description': 'Show cubes overlay',
            'expected_result': 'success'
        },
        {
            'command': 'actions.sleep(1)',
            'description': 'Wait for overlay to appear',
            'expected_result': 'success'
        },
        {
            'command': 'actions.user.hide_cubes()',
            'description': 'Hide cubes overlay',
            'expected_result': 'success'
        }
    ]
    
    return test_gaming_workflow("moonlight", commands, "comprehensive_cubes_test")