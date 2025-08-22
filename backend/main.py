from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from services import transcription, translation, dubbing, seo, scheduling, youtube_upload, tiktok_upload
from utils import storage, format
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
import os

app = FastAPI(title="IA Coach Vidéo Multiplateforme")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

os.makedirs("output", exist_ok=True)
app.mount("/output", StaticFiles(directory="output"), name="output")

@app.post("/process")
async def process_video(file: UploadFile = File(...), target_lang: str = Form("en")):
    video_path = storage.save_upload(file)
    text = transcription.transcribe(video_path)
    translated = translation.translate_text(text, target_lang)
    audio_path = dubbing.generate_voice(translated, target_lang)

    clip = VideoFileClip(video_path)
    sub = TextClip(translated, fontsize=40, color='white', bg_color='black', size=(clip.w, None), method="caption")\
        .set_duration(clip.duration).set_position(('center', 'bottom'))
    video_with_sub = CompositeVideoClip([clip, sub])
    narration = AudioFileClip(audio_path)
    final = video_with_sub.set_audio(narration)

    final_path = f"output/final_{target_lang}.mp4"
    final.write_videofile(final_path, codec="libx264", audio_codec="aac")

    vertical_path = format.convert_to_vertical(final_path, f"output/final_vertical_{target_lang}.mp4")
    seo_data = seo.generate_metadata(translated)
    best_time = scheduling.best_publish_time()

    yt_url = youtube_upload.upload_video(final_path, seo_data["title"], seo_data["description"], seo_data["tags"], publish_time=best_time, privacy="private")
    tt_url = tiktok_upload.upload_to_tiktok(vertical_path, seo_data["description"] + " " + " ".join(["#" + tag for tag in seo_data["tags"][:5]]))

    return {
        "transcription": text,
        "translation": translated,
        "final_video": f"/{final_path}",
        "youtube_url": yt_url,
        "tiktok_url": tt_url,
        "seo": seo_data,
        "publish_time": best_time
    }
