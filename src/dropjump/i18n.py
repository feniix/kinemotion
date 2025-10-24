"""Internationalization (i18n) support for kinemetry."""

import gettext
import locale
from pathlib import Path

# Global translation object
_translator: gettext.NullTranslations | None = None


def _(message: str) -> str:
    """
    Translate a message to the currently configured language.

    Args:
        message: English message to translate

    Returns:
        Translated message (or original if no translation available)
    """
    global _translator
    if _translator is None:
        return message
    return _translator.gettext(message)


def setup_i18n(language: str | None = None) -> None:
    """
    Set up internationalization support.

    Args:
        language: Language code (e.g., 'es', 'en'). If None, uses system locale.
    """
    global _translator

    # Determine language to use
    if language is None:
        # Try to get system locale
        try:
            system_locale, _ = locale.getdefaultlocale()
            language = system_locale.split("_")[0] if system_locale else "en"
        except Exception:
            language = "en"

    # If English, use null translator (no translation needed)
    if language == "en":
        _translator = None
        return

    # Find locales directory
    # When installed: site-packages/dropjump/locales
    # When developing: src/dropjump/locales
    module_dir = Path(__file__).parent
    locales_dir = module_dir / "locales"

    # Try to load translation catalog
    try:
        _translator = gettext.translation(
            "kinemetry",  # Domain name
            localedir=str(locales_dir),
            languages=[language],
            fallback=True,
        )
    except Exception:
        # Fallback to null translator
        _translator = None


def get_available_languages() -> list[str]:
    """
    Get list of available language codes.

    Returns:
        List of language codes (e.g., ['en', 'es'])
    """
    languages = ["en"]  # English always available

    # Find locales directory
    module_dir = Path(__file__).parent
    locales_dir = module_dir / "locales"

    if not locales_dir.exists():
        return languages

    # Find all language directories
    for lang_dir in locales_dir.iterdir():
        if lang_dir.is_dir() and (lang_dir / "LC_MESSAGES" / "kinemetry.mo").exists():
            languages.append(lang_dir.name)

    return sorted(languages)


# Initialize with system default
setup_i18n()
