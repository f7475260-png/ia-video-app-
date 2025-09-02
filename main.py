import os
import random
import numpy as np
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, ColorClip, concatenate_videoclips
import cv2
import argparse
from PIL import Image, ImageDraw
import tempfile
import time
import math
import re
from collections import Counter

class VideoAICreator:
    def __init__(self):
        self.video_clips = []
        self.audio_path = ""
        self.subtitles = []
        self.output_path = "assets/output/final_video.mp4"
        
        # Créer les répertoires nécessaires
        os.makedirs("assets/output", exist_ok=True)
        os.makedirs("assets/backgrounds", exist_ok=True)
        
        # Mots-clés d'arrêt simplifiés (pas besoin de NLTK)
        self.stopwords_fr = {'le', 'la', 'les', 'de', 'des', 'du', 'et', 'est', 'que', 'dans', 'pour', 'sur', 'avec'}
    
    def create_background_videos(self):
        """Crée 20 vidéos d'arrière-plan (version simplifiée)"""
        backgrounds_dir = "assets/backgrounds"
        
        if os.path.exists(backgrounds_dir) and len(os.listdir(backgrounds_dir)) >= 20:
            print("✓ Vidéos d'arrière-plan déjà existantes")
            return
        
        print("Création des vidéos d'arrière-plan...")
        
        for i in range(20):
            self.generate_simple_background(f"{backgrounds_dir}/bg_{i+1}.mp4")
            print(f"Création vidéo {i+1}/20...")
        
        print("✓ Vidéos d'arrière-plan créées!")
    
    def generate_simple_background(self, output_path, duration=5):
        """Version simplifiée pour générer une vidéo"""
        width, height = 640, 360  # Taille réduite pour plus de rapidité
        fps = 24
        total_frames = int(duration * fps)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame_idx in range(total_frames):
            # Créer un frame avec dégradé animé
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            t = frame_idx / total_frames * 2 * math.pi
            
            for y in range(height):
                for x in range(width):
                    r = int(128 + 127 * math.sin(x/50 + t))
                    g = int(128 + 127 * math.sin(y/50 + t))
                    b = int(128 + 127 * math.sin((x+y)/100 + t))
                    frame[y, x] = [b, g, r]
            
            out.write(frame)
        
        out.release()
    
    def analyze_text_context(self, text):
        """Analyse simplifiée du texte"""
        words = text.lower().split()
        words = [word for word in words if word.isalpha() and word not in self.stopwords_fr]
        
        word_freq = Counter(words)
        top_keywords = [word for word, count in word_freq.most_common(5)]
        
        # Catégories simplifiées
        if any(word in ['nature', 'arbre', 'plante', 'ciel'] for word in top_keywords):
            category = 'nature'
        elif any(word in ['tech', 'ordinateur', 'digital', 'internet'] for word in top_keywords):
            category = 'tech'
        else:
            category = 'abstract'
        
        return category, top_keywords
    
    def get_background_video(self, category):
        """Sélectionne une vidéo d'arrière-plan"""
        backgrounds_dir = "assets/backgrounds"
        if os.path.exists(backgrounds_dir):
            videos = [f for f in os.listdir(backgrounds_dir) if f.endswith('.mp4')]
            if videos:
                return os.path.join(backgrounds_dir, random.choice(videos))
        
        # Fallback: créer une vidéo colorée simple
        return self.create_color_background()
    
    def create_color_background(self, duration=5):
        """Crée une vidéo de couleur unie"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        clip = ColorClip(size=(640, 360), color=color, duration=duration)
        clip.write_videofile(temp_path, fps=24, verbose=False, logger=None)
        clip.close()
        
        return temp_path
    
    def text_to_speech(self, text):
        """Solution de contournement pour la voix off"""
        try:
            # Utiliser un système de texte-à-parole simple
            print("🎵 Génération de la voix off...")
            
            # Créer un fichier audio silencieux (solution temporaire)
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                self.audio_path = tmp_file.name
            
            # Estimer la durée basée sur le texte
            duration = max(3, len(text.split()) / 3)
            
            # Créer un audio silencieux
            silent_clip = AudioFileClip.silent(duration=duration)
            silent_clip.write_audiofile(self.audio_path, fps=22050, verbose=False, logger=None)
            silent_clip.close()
            
            print("✓ Audio préparé (mode silencieux)")
            return True
            
        except Exception as e:
            print(f"✗ Erreur audio: {e}")
            return False
    
    def generate_subtitles(self, text, audio_duration):
        """Génère des sous-titres simples"""
        phrases = [p.strip() + '.' for p in text.split('.') if p.strip()]
        
        if not phrases:
            return []
        
        subtitle_duration = audio_duration / len(phrases) if audio_duration > 0 else 3
        
        self.subtitles = []
        for i, phrase in enumerate(phrases):
            if phrase.strip():
                start_time = i * subtitle_duration
                end_time = (i + 1) * subtitle_duration
                self.subtitles.append({
                    'text': phrase,
                    'start': start_time,
                    'end': end_time,
                    'duration': subtitle_duration
                })
        
        print(f"✓ {len(self.subtitles)} sous-titres générés")
        return self.subtitles
    
    def create_video(self, text, video_style="youtube", duration=30):
        """Crée la vidéo finale (version simplifiée)"""
        print("🚀 Démarrage de la création...")
        
        # 1. Créer les backgrounds si nécessaire
        self.create_background_videos()
        
        # 2. Analyse du contexte
        category, keywords = self.analyze_text_context(text)
        print(f"📊 Catégorie: {category}")
        
        # 3. Préparer l'audio
        if not self.text_to_speech(text):
            print("⚠️ Mode silencieux activé")
            # Durée par défaut
            audio_duration = min(30, max(5, len(text.split()) / 2))
        else:
            try:
                audio_clip = AudioFileClip(self.audio_path)
                audio_duration = audio_clip.duration
                audio_clip.close()
            except:
                audio_duration = 10
        
        # 4. Générer les sous-titres
        self.generate_subtitles(text, audio_duration)
        
        # 5. Sélectionner les vidéos d'arrière-plan
        video_clips = []
        current_duration = 0
        
        while current_duration < audio_duration:
            video_path = self.get_background_video(category)
            
            try:
                clip = VideoFileClip(video_path)
                clip_duration = min(clip.duration, audio_duration - current_duration)
                
                if clip_duration > 0:
                    clip = clip.subclip(0, clip_duration)
                    video_clips.append(clip)
                    current_duration += clip_duration
                
            except Exception as e:
                print(f"⚠️ Erreur vidéo, utilisation fallback: {e}")
                fallback_clip = ColorClip(size=(640, 360), color=(
                    random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                ), duration=min(3, audio_duration - current_duration))
                video_clips.append(fallback_clip)
                current_duration += 3
        
        # 6. Assemblage final
        if not video_clips:
            print("✗ Aucune séquence vidéo")
            return False
        
        try:
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Ajouter l'audio si disponible
            if os.path.exists(self.audio_path):
                audio = AudioFileClip(self.audio_path)
                final_video = final_video.set_audio(audio)
            
            # Ajouter les sous-titres
            subtitle_clips = []
            for subtitle in self.subtitles:
                try:
                    # Créer un texte simple
                    txt_clip = TextClip(
                        subtitle['text'], 
                        fontsize=24, 
                        color='white', 
                        bg_color='black',
                        size=(final_video.w * 0.9, None)
                    )
                    txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(
                        subtitle['start']).set_duration(subtitle['duration'])
                    subtitle_clips.append(txt_clip)
                except:
                    continue
            
            if subtitle_clips:
                final_video = CompositeVideoClip([final_video] + subtitle_clips)
            
            # Export final
            final_video.write_videofile(
                self.output_path, 
                fps=24, 
                verbose=False,
                logger=None
            )
            
            print(f"✅ Vidéo créée: {self.output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Erreur final: {e}")
            return False
        finally:
            # Nettoyage
            try:
                for clip in video_clips:
                    clip.close()
            except:
                pass

def main():
    parser = argparse.ArgumentParser(description="Créateur de vidéos simple")
    parser.add_argument("--text", type=str, help="Texte pour la vidéo")
    parser.add_argument("--output", type=str, default="assets/output/video.mp4", help="Fichier de sortie")
    
    args = parser.parse_args()
    
    if not args.text:
        args.text = "Bienvenue dans votre vidéo générée par IA"
    
    print("🎬 Video AI Creator - Version Simplifiée")
    print("========================================")
    
    creator = VideoAICreator()
    creator.output_path = args.output
    
    success = creator.create_video(args.text)
    
    if success:
        print("\n🎉 Succès! Votre vidéo est prête!")
        print(f"📁 Emplacement: {args.output}")
    else:
        print("\n❌ La création a échoué")

if __name__ == "__main__":
    main()
