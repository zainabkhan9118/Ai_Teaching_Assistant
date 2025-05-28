"""
Translation and language utilities
"""

from config.languages import LANGUAGES


def get_translation(key, language="fr"):
    """Translation function with fallback"""
    # Default to French if language is not available
    if language not in LANGUAGES:
        language = "fr"
    return LANGUAGES[language]['translations'].get(key, key)
