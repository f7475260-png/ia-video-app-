from gtts import gTTS
import os

def generate_voice(text: str, lang: str) -> str:
    os.makedirs("output", exist_ok=True)
    file_path = f"output/voice_{lang}.mp3"
    gTTS(text=text, lang=lang).save(file_path)
    return file_path
