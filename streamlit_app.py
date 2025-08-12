import streamlit as st
from utils.video_generator import generate_video
import os

st.set_page_config(page_title="🎬 Générateur de Vidéo IA", layout="centered")

st.title("🎬 Générateur de Vidéo IA")
st.markdown("Crée ta propre vidéo à partir d'un thème, en quelques clics.")

with st.form("video_form"):
    theme = st.text_input("🎯 Thème de la vidéo", "voyage au Japon")
    duration = st.slider("⏱️ Durée (secondes)", min_value=10, max_value=180, value=60)
    language = st.selectbox("🗣️ Langue", ["fr", "en"])
    format_type = st.selectbox("🎥 Format", ["youtube", "tiktok", "short"])
    music_enabled = st.checkbox("🎵 Ajouter musique de fond", value=True)
    submitted = st.form_submit_button("🚀 Générer la vidéo")

if submitted:
    st.info("Génération en cours...")
    try:
        video_path = generate_video({
            "theme": theme,
            "duration": duration,
            "language": language,
            "format": format_type,
            "music": music_enabled
        })

        if os.path.exists(video_path):
            st.success("✅ Vidéo générée avec succès !")
            st.video(video_path)

            with open(video_path, "rb") as f:
                st.download_button("📥 Télécharger la vidéo", data=f, file_name=os.path.basename(video_path), mime="video/mp4")
        else:
            st.error("La vidéo n'a pas pu être trouvée ou générée.")
    except Exception as e:
        st.error(f"Erreur lors de la génération : {str(e)}")
