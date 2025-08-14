# 🎬 InVideo-like Streamlit App

Génère automatiquement des vidéos multi-scènes à partir d'une idée :
- FR/EN (gTTS)
- Formats 9:16 (TikTok/Shorts) & 16:9 (YouTube)
- Résolutions 360p→1080p
- Musique optionnelle (upload)
- Stock-footage automatique (Pexels/Pixabay API)
- Sous-titres: SRT + hard-burn (overlay PIL, pas d’ImageMagick)

## Déploiement Streamlit Cloud
1) Crée un repo GitHub avec `app.py`, `requirements.txt`, `packages.txt`, `.gitignore`, `README.md`
2) Sur Streamlit Cloud: **New app** → connecte ton repo
3) Dans **Secrets** ajoute:
