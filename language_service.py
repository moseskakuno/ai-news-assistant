
SUPPORTED_LANGUAGES = {
    "English": "English",
    "German": "German",
    "French": "French",
    "Spanish": "Spanish",
    "Portuguese": "Portuguese",
    "Arabic": "Arabic",
    "Hindi": "Hindi",
    "Japanese": "Japanese",
    "Dhivehi": "Dhivehi",
    "Chinese": "Simplified Chinese",
}


def get_supported_languages():
    """Return the available digest languages."""

    return list(SUPPORTED_LANGUAGES.keys())


def get_language_instruction(language):
    """
    Return the AI writing instruction for the selected language.
    """

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {language}"
        )

    language_name = SUPPORTED_LANGUAGES[language]

    return (
        f"Write the entire news digest in {language_name}. "
        "Preserve the original meaning of the supplied "
        "information and do not invent or add facts."
    )
