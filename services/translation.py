def translate_text(text: str, target_lang: str) -> str:
    translations = {
        "en": "This is a demo translation of your video.",
        "fr": text,
        "es": "Esta es una traducción de demostración.",
        "de": "Dies ist eine Demo-Übersetzung."
    }
    return translations.get(target_lang.lower(), text)
