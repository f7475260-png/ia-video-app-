def generate_metadata(text: str) -> dict:
    words = text.split()
    tags = list(set([w.lower().strip(".,") for w in words if len(w) > 4]))
    return {
        "title": f"Vidéo sur {tags[0] if tags else 'IA'}",
        "description": f"Découvrez cette vidéo: {text}",
        "tags": tags
    }
