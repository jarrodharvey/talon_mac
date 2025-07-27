"""
Homophone support for OCR text matching.

Provides fallback homophone definitions when community homophones are unavailable.
"""

from talon import actions

# Basic homophones for common speech recognition errors (fallback if community system unavailable)
BASIC_HOMOPHONES = {
    "to": ["too", "two"],
    "too": ["to", "two"], 
    "two": ["to", "too"],
    "there": ["their", "they're"],
    "their": ["there", "they're"],
    "they're": ["there", "their"],
    "your": ["you're"],
    "you're": ["your"],
    "its": ["it's"],
    "it's": ["its"],
    "here": ["hear"],
    "hear": ["here"],
    "break": ["brake"],
    "brake": ["break"],
    "right": ["write", "rite"],
    "write": ["right", "rite"],
    "rite": ["right", "write"],
    "no": ["know"],
    "know": ["no"],
    "one": ["won"],
    "won": ["one"],
    "four": ["for", "fore"],
    "for": ["four", "fore"],
    "fore": ["four", "for"],
    "eight": ["ate"],
    "ate": ["eight"],
    "wait": ["weight"],
    "weight": ["wait"],
    "buy": ["by", "bye"],
    "by": ["buy", "bye"],
    "bye": ["buy", "by"]
}

def get_homophones_for_word(word: str) -> list:
    """Get homophones using community system with fallback to basic set"""
    try:
        # Try community homophones system first
        homophones = actions.user.homophones_get(word.lower())
        if homophones and len(homophones) > 1:
            return homophones
    except:
        pass
    
    # Fallback to basic homophones
    return BASIC_HOMOPHONES.get(word.lower(), [word])

def get_all_homophones() -> dict:
    """Get all available homophones (for debugging or testing)"""
    return BASIC_HOMOPHONES.copy()