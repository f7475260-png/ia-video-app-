# Générateur de Vidéo IA

Crée des vidéos automatiquement à partir d’un thème: script IA, voix off, images d’arrière-plan, musique et montage exporté en MP4.

## Prérequis
- Python 3.9+
- FFmpeg installé (obligatoire)

## Installation
pip install -r requirements.txt

## Configuration
Créer un fichier `.env`:
HUGGINGFACE_API_KEY=ta_cle
HF_MODEL_ID=gpt2

## Lancer (Flask)
python app.py  # http://localhost:7860

## Lancer (Streamlit)
streamlit run streamlit_app.py

## Dossiers
- assets/images : images .jpg/.png
- assets/music : musiques .mp3
- output : vidéos générées

## Déploiement
- Streamlit Cloud : connecter le repo et lancer streamlit_app.py
- Hugging Face Spaces : créer un Space Streamlit et pousser ce projet
- Render : utiliser render.yaml pour démarrer un service web Python

## Astuces
- Durée conseillée: 30–90s
- Volumes: musique à 8–15% pour garder la voix claire
- Images: 1080x1920 (vertical) ou 1920x1080 (horizontal) selon format
