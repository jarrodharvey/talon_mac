tag: user.claude_helpers

-

troubleshoot cubes [<user.word>]:
    user.test_cubes_in_moonlight(word or None)

troubleshoot command <user.word> in <user.word>:
    user.test_command_with_words(word_1, word_2)

troubleshoot show cubes:
    user.test_command_in_app("moonlight", "actions.user.show_cubes()", "Show cubes overlay")

troubleshoot hide cubes:
    user.test_command_in_app("moonlight", "actions.user.hide_cubes()", "Hide cubes overlay")

troubleshoot focus <user.word>:
    user.troubleshooter.focus_application(word)

troubleshoot return:
    user.troubleshooter.return_to_terminal()

troubleshoot screenshot:
    path = user.troubleshooter.capture_screenshot("_manual")
    print("Screenshot saved: " + path)

troubleshoot logs:
    logs = user.troubleshooter.check_talon_logs(30)
    print("Recent Talon logs:")
    print(logs)