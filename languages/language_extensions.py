"""
Extends the community language system with custom languages.
This must load AFTER community/core/modes/ but BEFORE language contexts activate.
"""
from talon import Module

# Import the community modules we need to patch
from ...community.core.modes import code_languages
from ...community.core.modes import language_modes

mod = Module()

# Define custom languages to add
CUSTOM_LANGUAGES = [
    code_languages.Language(
        id="mermaid",
        spoken_form=["mermaid", "mermaid diagram"],
        extensions=["mmd", "mermaid"]
    ),
    # Future languages can be added here:
    # code_languages.Language("graphviz", "graph viz", ["dot", "gv"]),
]

# Extend the code_languages list
code_languages.code_languages.extend(CUSTOM_LANGUAGES)

# Rebuild derived data structures that were built at module load time

# 1. Rebuild user.language_mode list (spoken forms -> language IDs)
language_modes.ctx.lists["user.language_mode"] = {
    spoken_form: language.id
    for language in code_languages.code_languages
    for spoken_form in language.spoken_forms
}

# 2. Rebuild extension_lang_map (file extensions -> language IDs)
language_modes.extension_lang_map = {
    f".{ext}": lang.id
    for lang in code_languages.code_languages
    for ext in lang.extensions
}

# 3. Rebuild language_ids set (used for validation in code_set_language_mode)
language_modes.language_ids = {
    lang.id for lang in code_languages.code_languages
}
