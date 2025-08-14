import os
import io
import json
import time
import uuid
import math
import tempfile
import requests
from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np
from gtts import gTTS
from pydub import AudioSegment
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips,
    ColorClip, ImageClip
)
from PIL import Image, ImageDraw, ImageFont

import streamlit as st

# ========== CONFIG ==========
# Clés d'API via Streamlit Secrets (Settings > Secrets sur Cloud)
# st.secrets["OPENAI_API_KEY"]
# st.secrets["PEXELS_API_KEY"]
# st.secrets["PIXABAY_API_KEY"]

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
PEXELS_API_KEY = st.secrets.get("PEXELS_API_KEY", "")
PIXABAY_API_KEY = st.secrets.get("PIXABAY_API_KEY", "")

# Durée max (secondes)
MAX_DURATION = 10 * 60

# Dossier temp
TMP = Path(tempfile.gettempdir()) / "invideo_clone"
TMP.mkdir(exist_ok=True)

# ========== UI ==========
st.set_page_config(page_title="InVideo-like Generator", page_icon="🎬", layout="centered")
st.title("🎬 Générateur de vidéos IA (style InVideo)")

idea = st.text_area("💡 Décris ton idée (FR ou EN)", placeholder="Ex: Un mini-guide motivant sur reprendre le sport après une pause.")
language = st.selectbox("Langue de narration", ["fr", "en"], index=0)

col1, col2 = st.columns(2)
with col1:
    target_format = st.selectbox("Format", ["TikTok / Shorts (9:16)", "YouTube (16:9)"])
with col2:
    base_res = st.selectbox("Résolution de base", ["360p", "480p", "720p", "1080p"], index=2)

duration = st.slider("Durée totale (secondes)", 10, MAX_DURATION, 60, step=5)

music_file = st.file_uploader("🎵 Musique de fond (MP3/WAV) — optionnel", type=["mp3", "wav"])
generate_btn = st.button("🚀 Générer la vidéo")

# ========== UTIL ==========
def pick_resolution(fmt: str, res_label: str) -> Tuple[int, int]:
    res_map = {"360p": 360, "480p": 480, "720p": 720, "1080p": 1080}
    h = res_map[res_label]
    if "9:16" in fmt:
        # vertical
        w = int(h * 9 / 16 * 16)  # multiple of 16
        return (w, h)
    else:
        # horizontal 16:9
        w = int(h * 16 / 9 // 2 * 2)
        return (w, h)

def tts_gtts(text: str, lang: str) -> AudioSegment:
    tts = gTTS(text=text, lang=lang)
    p = TMP / f"tts_{uuid.uuid4().hex}.mp3"
    tts.save(str(p))
    return AudioSegment.from_file(p)

def normalize_audio(aud: AudioSegment, target_dbfs=-16.0) -> AudioSegment:
    change = target_dbfs - aud.dBFS
    return aud.apply_gain(change)

def duck_music(voice: AudioSegment, music: AudioSegment, duck_db=18) -> AudioSegment:
    # boucle musique pour couvrir la voix
    if len(music) < len(voice):
        loops = int(len(voice) / len(music)) + 2
        music = music * loops
    music = music[:len(voice)].apply_gain(-duck_db)
    return music.overlay(voice)

def draw_subtitle_image(text: str, width: int, height: int,
                        pad=32, box_opacity=180, font_size=42,
                        font_name="DejaVuSans.ttf") -> Image.Image:
    """
    Crée une image transparente de la largeur de la vidéo, posée en bas,
    avec un bandeau sombre et le texte en blanc (multi-lignes).
    """
    # hauteur de bande estimée
    band_h = int(height * 0.18)
    img = Image.new("RGBA", (width, band_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # fond noir semi-opaque
    draw.rectangle([(0, 0), (width, band_h)], fill=(0, 0, 0, box_opacity))

    # police
    try:
        font = ImageFont.truetype(font_name, font_size)
    except:
        font = ImageFont.load_default()

    # wrap du texte
    max_text_width = width - 2 * pad
    lines = []
    words = text.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        tw, th = draw.textbbox((0, 0), test, font=font)[2:]
        if tw <= max_text_width:
            line = test
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)

    # dessiner centré verticalement
    total_text_h = sum(draw.textbbox((0,0), ln, font=font)[3] for ln in lines) + (len(lines)-1)*8
    y = (band_h - total_text_h) // 2
    for ln in lines:
        tw, th = draw.textbbox((0, 0), ln, font=font)[2:]
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=(255, 255, 255, 255), font=font)
        y += th + 8

    return img

def overlay_subtitles(clip: VideoFileClip, text: str) -> CompositeVideoClip:
    w, h = clip.w, clip.h
    img = draw_subtitle_image(text, w, h)
    png_path = TMP / f"sub_{uuid.uuid4().hex}.png"
    img.save(png_path)
    sub_clip = ImageClip(str(png_path)).set_duration(clip.duration).set_position(("center", "bottom"))
    return CompositeVideoClip([clip, sub_clip])

def search_stock_video_pexels(query: str, orientation: str = "portrait", max_dur_s: int = 30) -> str:
    """
    Retourne une URL mp4 (qualité medium) depuis Pexels selon la requête.
    """
    if not PEXELS_API_KEY:
        return ""
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 1, "orientation": orientation}
    r = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=20)
    if r.status_code != 200:
        return ""
    data = r.json()
    if not data.get("videos"):
        return ""
    vid = data["videos"][0]
    # choisir une qualité mp4
    files = vid.get("video_files", [])
    files = sorted(files, key=lambda x: x.get("height", 0))  # plus petit d'abord
    for f in files:
        link = f.get("link", "")
        if link.endswith(".mp4"):
            return link
    return ""

def search_stock_video_pixabay(query: str, orientation: str = "vertical") -> str:
    """
    Retourne une URL mp4 depuis Pixabay selon la requête.
    """
    if not PIXABAY_API_KEY:
        return ""
    params = {"key": PIXABAY_API_KEY, "q": query, "video_type": "film", "per_page": 3, "safesearch": "true"}
    if orientation == "vertical":
        params["orientation"] = "vertical"
    r = requests.get("https://pixabay.com/api/videos/", params=params, timeout=20)
    if r.status_code != 200:
        return ""
    data = r.json()
    hits = data.get("hits", [])
    if not hits:
        return ""
    # prendre la plus petite variante pour limiter poids
    videos = hits[0].get("videos", {})
    for k in ["small", "tiny", "medium"]:
        if k in videos and "url" in videos[k]:
            return videos[k]["url"]
    return ""

def download_file(url: str) -> Path:
    p = TMP / f"dl_{uuid.uuid4().hex}.mp4"
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(p, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return p

def safe_video_clip(path: Path, target_wh: Tuple[int,int], scene_len: float) -> VideoFileClip:
    """
    Charge la vidéo, la coupe à scene_len, et l’adapte à target_wh avec letterbox.
    """
    w, h = target_wh
    clip = VideoFileClip(str(path)).subclip(0, min(scene_len,  clip_duration(path)))
    # Resize + Letterbox
    clip = clip.resize(width=w) if clip.w/clip.h >= w/h else clip.resize(height=h)
    # ajouter bandes si besoin
    clip = clip.on_color(size=(w, h), color=(0,0,0), pos='center')
    return clip

def clip_duration(path: Path) -> float:
    try:
        return VideoFileClip(str(path)).duration
    except:
        return 5.0

def text_summarizer_to_scenes(idea_text: str, lang: str, total_duration: float) -> List[Dict]:
    """
    Utilise un LLM (clé OPENAI via secrets) pour créer 4-8 scènes courtes.
    Si pas de clé, fallback simple.
    """
    target_scenes = 6
    if not OPENAI_API_KEY:
        # Fallback: 5 scènes simples basé sur l'idée
        base = idea_text.strip() or ("Vidéo " + ("FR" if lang=="fr" else "EN"))
        return [{"narration": base, "visual": "generic background of the topic"}] * 5

    import openai
    openai.api_key = OPENAI_API_KEY
    sys_prompt = (
        "You are a concise video planner. Split the user's idea into 4-8 short scenes. "
        "For each scene, produce 'narration' (<=25 words) in the target language and "
        "'visual' (2-6 keywords for stock-footage search). Return pure JSON list."
    )
    user_prompt = json.dumps({
        "language": "fr" if lang=="fr" else "en",
        "idea": idea_text
    })
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": sys_prompt},
                  {"role": "user", "content": user_prompt}],
        temperature=0.7
    )
    txt = resp.choices[0].message["content"]
    try:
        scenes = json.loads(txt)
        if isinstance(scenes, list) and 4 <= len(scenes) <= 8:
            return scenes
    except:
        pass
    # secours
    return [{"narration": idea_text[:120], "visual": "motivational people running sunrise"}] * 5

def build_srt(subs: List[Tuple[float, float, str]]) -> str:
    """
    Crée le contenu SRT (index, start --> end, text)
    """
    def ts(t):
        # t en secondes -> "HH:MM:SS,mmm"
        h = int(t // 3600); t -= h*3600
        m = int(t // 60);   t -= m*60
        s = int(t);         ms = int(round((t - s)*1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, (start, end, text) in enumerate(subs, 1):
        lines += [str(i), f"{ts(start)} --> {ts(end)}", text, ""]
    return "\n".join(lines)

def ensure_font_package():
    """
    Sur Streamlit Cloud, installer un set de polices n’est pas garanti.
    On essaie d’utiliser DejaVu (souvent dispo); sinon PIL default.
    """
    return "DejaVuSans.ttf"

# ========== PIPELINE ==========
if generate_btn:
    if not idea.strip():
        st.error("Merci d’entrer une idée.")
        st.stop()

    W, H = pick_resolution(target_format, base_res)

    with st.spinner("Découpage de l’idée en scènes…"):
        scenes = text_summarizer_to_scenes(idea, language, duration)

    # Répartition de la durée entre scènes (égale + marge)
    n = max(1, len(scenes))
    per_scene = duration / n

    # AUDIO global (voix + musique)
    voice_tracks = []
    srt_items = []
    t0 = 0.0

    font_name = ensure_font_package()

    with st.spinner("Génération de la voix et des sous-titres…"):
        for s in scenes:
            narration = s.get("narration", "").strip() or " "
            # TTS
            v = tts_gtts(narration, language)
            v = normalize_audio(v)
            v = v[:int(per_scene*1000)]
            voice_tracks.append(v)

    # Musique optionnelle
    music_track = None
    if music_file is not None:
        try:
            mf = AudioSegment.from_file(music_file)
            music_track = normalize_audio(mf, -20.0)
        except Exception as e:
            st.warning(f"Musique ignorée (erreur lecture): {e}")

    # Mixage AUDIO et chronologie SRT
    with st.spinner("Mixage audio…"):
        timeline = AudioSegment.silent(duration=int(duration*1000))
        cursor_ms = 0
        for i, (seg, s) in enumerate(zip(voice_tracks, scenes)):
            seg_len = len(seg)
            if music_track:
                seg = duck_music(seg, music_track[:seg_len])
            timeline = timeline.overlay(seg, position=cursor_ms)
            # SRT : un bloc par scène sur sa fenêtre
            start_s = cursor_ms / 1000.0
            end_s = (cursor_ms + seg_len) / 1000.0
            srt_items.append((start_s, end_s, s.get("narration","")))
            cursor_ms += int(per_scene*1000)

        # Sauvegarde audio final
        audio_path = TMP / f"final_audio_{uuid.uuid4().hex}.mp3"
        timeline.export(audio_path, format="mp3")

        # Sauvegarde SRT
        srt_text = build_srt(srt_items)
        srt_path = TMP / f"subs_{uuid.uuid4().hex}.srt"
        srt_path.write_text(srt_text, encoding="utf-8")

    # VIDEO par scène
    clips = []
    orientation = "portrait" if "9:16" in target_format else "landscape"
    with st.spinner("Sélection des vidéos libres & montage…"):
        cursor_s = 0.0
        for i, s in enumerate(scenes):
            query = s.get("visual", "") or s.get("narration", "")
            # chercher d'abord Pexels, puis fallback Pixabay
            url = search_stock_video_pexels(query, orientation=("portrait" if "9:16" in target_format else "landscape"))
            if not url:
                url = search_stock_video_pixabay(query, orientation=("vertical" if "9:16" in target_format else "horizontal"))

            scene_len = per_scene

            if url:
                try:
                    p = download_file(url)
                    base_clip = safe_video_clip(p, (W, H), scene_len)
                except Exception as e:
                    st.warning(f"Clip introuvable ou erreur download ({query}) → fond neutre. Détail: {e}")
                    base_clip = ColorClip(size=(W, H), color=(0,0,0)).set_duration(scene_len)
            else:
                # fallback fond neutre si rien trouvé
                base_clip = ColorClip(size=(W, H), color=(0,0,0)).set_duration(scene_len)

            # Sous-titre hard-burn (overlay PIL) sur chaque scène
            sub_text = s.get("narration","")
            base_clip = overlay_subtitles(base_clip, sub_text)

            clips.append(base_clip)
            cursor_s += scene_len

    # Assemblage + audio
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip = final_clip.set_audio(AudioFileClip(str(audio_path)))

    # Export
    out_path = TMP / f"video_{uuid.uuid4().hex}.mp4"
    with st.spinner("Encodage final (ffmpeg)…"):
        # fps 24, h264 + aac
        final_clip.write_videofile(str(out_path), fps=24, codec="libx264", audio_codec="aac", threads=4, logger=None)

    st.success("✅ Vidéo prête !")
    st.video(str(out_path))

    with open(out_path, "rb") as f:
        st.download_button("📥 Télécharger MP4", f, file_name="video_ai.mp4", mime="video/mp4")

    st.download_button("📄 Télécharger sous-titres (SRT)", data=srt_path.read_text(encoding="utf-8"),
                       file_name="subtitles.srt", mime="text/plain")

    st.info("Astuce : tu peux uploader la vidéo MP4 et le fichier SRT sur YouTube/TikTok. Les sous‑titres seront reconnus.")
