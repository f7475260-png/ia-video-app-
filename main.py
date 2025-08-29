import os
import random
import numpy as np
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, ColorClip, concatenate_videoclips
import gtts
import cv2
import argparse
from PIL import Image, ImageDraw, ImageFont
import tempfile
import time
import math
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import threading

# Télécharger les ressources NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class VideoAICreator:
    def __init__(self):
        self.video_clips = []
        self.audio_path = ""
        self.subtitles = []
        self.output_path = "assets/output/final_video.mp4"
        self.stopwords_fr = set(stopwords.words('french'))
        
        # Créer les répertoires nécessaires
        os.makedirs("assets/output", exist_ok=True)
        os.makedirs("assets/backgrounds", exist_ok=True)
        
        # Générer les vidéos d'arrière-plan intégrées
        self.create_background_videos()
    
    def create_background_videos(self):
        """Crée 1000 vidéos d'arrière-plan intégrées dans le code"""
        backgrounds_dir = "assets/backgrounds"
        
        # Vérifier si les vidéos d'arrière-plan existent déjà
        if os.path.exists(backgrounds_dir) and len(os.listdir(backgrounds_dir)) >= 1000:
            print("✓ 1000 vidéos d'arrière-plan déjà existantes")
            return
            
        print("Création de 1000 vidéos d'arrière-plan...")
        os.makedirs(backgrounds_dir, exist_ok=True)
        
        # Créer 1000 vidéos d'arrière-plan différentes en multithread
        threads = []
        videos_per_thread = 100
        
        for thread_idx in range(10):
            start_idx = thread_idx * videos_per_thread + 1
            end_idx = (thread_idx + 1) * videos_per_thread
            thread = threading.Thread(
                target=self.generate_videos_batch,
                args=(start_idx, end_idx, backgrounds_dir)
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        print("✓ 1000 vidéos d'arrière-plan créées avec succès!")
    
    def generate_videos_batch(self, start_idx, end_idx, backgrounds_dir):
        """Génère un batch de vidéos en parallèle"""
        for i in range(start_idx, end_idx + 1):
            self.generate_animated_background(f"{backgrounds_dir}/bg_{i}.mp4")
            if i % 10 == 0:
                print(f"Création de la vidéo {i}/1000...")
    
    def generate_animated_background(self, output_path, duration=8):
        """Génère une vidéo d'arrière-plan animée avec catégorie"""
        width, height = 1920, 1080
        fps = 24
        total_frames = int(duration * fps)
        
        # Catégories thématiques pour l'IA contextuelle
        categories = [
            'nature', 'technologie', 'ville', 'abstrait', 
            'cosmique', 'géométrique', 'couleurs', 'particules',
            'gradient', 'motivation'
        ]
        
        category = random.choice(categories)
        
        # Créer le writer vidéo
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame_idx in range(total_frames):
            if category == 'nature':
                frame = self.create_nature_effect(width, height, frame_idx, total_frames)
            elif category == 'technologie':
                frame = self.create_tech_effect(width, height, frame_idx, total_frames)
            elif category == 'ville':
                frame = self.create_city_effect(width, height, frame_idx, total_frames)
            elif category == 'cosmique':
                frame = self.create_cosmic_effect(width, height, frame_idx, total_frames)
            elif category == 'géométrique':
                frame = self.create_geometric_effect(width, height, frame_idx, total_frames)
            elif category == 'couleurs':
                frame = self.create_color_effect(width, height, frame_idx, total_frames)
            elif category == 'particules':
                frame = self.create_particle_effect(width, height, frame_idx, total_frames)
            elif category == 'gradient':
                frame = self.create_gradient_effect(width, height, frame_idx, total_frames)
            elif category == 'motivation':
                frame = self.create_motivation_effect(width, height, frame_idx, total_frames)
            else:  # abstrait
                frame = self.create_abstract_effect(width, height, frame_idx, total_frames)
            
            out.write(frame)
        
        out.release()
        
        # Ajouter des métadonnées de catégorie dans le nom de fichier
        new_path = output_path.replace('.mp4', f'_{category}.mp4')
        os.rename(output_path, new_path)
    
    def create_nature_effect(self, width, height, frame_idx, total_frames):
        """Effet nature - vert, bleu, couleurs naturelles"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        t = frame_idx / total_frames * 2 * math.pi
        
        # Ciel bleu avec渐变
        for y in range(height):
            blue = int(100 + 50 * math.sin(y/100 + t))
            green = int(150 + 50 * math.sin(y/80 + t))
            frame[y, :] = [blue, green, 200]  # BGR format
        
        # Ajouter des éléments naturels
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(height//2, height)
            size = random.randint(10, 50)
            color = (0, random.randint(100, 200), 0)  # Vert pour la végétation
            cv2.circle(frame, (x, y), size, color, -1)
        
        return frame
    
    def create_tech_effect(self, width, height, frame_idx, total_frames):
        """Effet technologie - bleu, circuits, données"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        t = frame_idx / total_frames * 2 * math.pi
        
        # Fond bleu technologique
        frame[:, :] = [100, 50, 30]  # Bleu foncé
        
        # Ajouter des lignes de circuit
        for i in range(5):
            y = int(height/2 + 100 * math.sin(t + i))
            cv2.line(frame, (0, y), (width, y), (255, 255, 100), 2)
        
        # Points de données
        for _ in range(100):
            x = random.randint(0, width)
            y = random.randint(0, height)
            cv2.circle(frame, (x, y), 2, (200, 200, 255), -1)
        
        return frame
    
    def create_city_effect(self, width, height, frame_idx, total_frames):
        """Effet ville - bâtiments, lumières"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Ciel nocturne
        frame[:, :] = [30, 30, 50]  # Bleu nuit
        
        # Bâtiments
        for i in range(10):
            building_width = random.randint(50, 200)
            building_height = random.randint(100, 400)
            x = random.randint(0, width - building_width)
            y = height - building_height
            
            color = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
            cv2.rectangle(frame, (x, y), (x + building_width, height), color, -1)
            
            # Fenêtres illuminées
            for _ in range(random.randint(5, 20)):
                wx = x + random.randint(10, building_width - 20)
                wy = y + random.randint(10, building_height - 20)
                if random.random() > 0.5:  # 50% de chances d'être allumé
                    cv2.rectangle(frame, (wx, wy), (wx + 10, wy + 15), (100, 200, 255), -1)
        
        return frame
    
    def create_cosmic_effect(self, width, height, frame_idx, total_frames):
        """Effet cosmique - espace, étoiles, nébuleuses"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        t = frame_idx / total_frames * 2 * math.pi
        
        # Fond spatial
        frame[:, :] = [20, 10, 40]  # Bleu très foncé
        
        # Étoiles
        for _ in range(300):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            cv2.circle(frame, (x, y), size, (brightness, brightness, brightness), -1)
        
        # Nébuleuse colorée
        center_x = width // 2 + int(100 * math.sin(t))
        center_y = height // 2 + int(100 * math.cos(t))
        
        for r in range(100, 300, 5):
            color = (
                random.randint(50, 200),
                random.randint(50, 200),
                random.randint(100, 255)
            )
            cv2.circle(frame, (center_x, center_y), r, color, 2)
        
        return frame
    
    def create_geometric_effect(self, width, height, frame_idx, total_frames):
        """Effet géométrique - formes, patterns"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        t = frame_idx / total_frames * 2 * math.pi
        
        # Fond coloré
        hue = int(180 * math.sin(t))  # Change de couleur
        frame[:, :] = [hue, 100, 100]
        
        # Formes géométriques animées
        for i in range(8):
            angle = i * math.pi / 4 + t
            x = int(width/2 + 200 * math.cos(angle))
            y = int(height/2 + 200 * math.sin(angle))
            
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            
            # Dessiner différentes formes
            if i % 3 == 0:
                cv2.circle(frame, (x, y), 60, color, -1)
            elif i % 3 == 1:
                pts = np.array([[x-50, y-50], [x+50, y-50], [x, y+50]], np.int32)
                cv2.fillPoly(frame, [pts], color)
            else:
                cv2.rectangle(frame, (x-40, y-40), (x+40, y+40), color, -1)
        
        return frame
    
    def create_color_effect(self, width, height, frame_idx, total_frames):
        """Effet de couleurs vibrantes"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        t = frame_idx / total_frames * 2 * math.pi
        
        # Pattern de couleurs changeantes
        for y in range(height):
            for x in range(width):
                r = int(128 + 127 * math.sin(x/50 + t))
                g = int(128 + 127 * math.sin(y/50 + t + math.pi/3))
                b = int(128 + 127 * math.sin((x+y)/100 + t + 2*math.pi/3))
                frame[y, x] = [b, g, r]
        
        return frame
    
    def create_particle_effect(self, width, height, frame_idx, total_frames):
        """Effet de particules animées"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        t = frame_idx / total_frames * 2 * math.pi
        
        # Particules avec mouvement
        for _ in range(200):
            x = int(width/2 + random.randint(-400, 400) * math.cos(t + random.random()))
            y = int(height/2 + random.randint(-400, 400) * math.sin(t + random.random()))
            
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            
            size = random.randint(2, 8)
            cv2.circle(frame, (x, y), size, color, -1)
        
        return frame
    
    def create_gradient_effect(self, width, height, frame_idx, total_frames):
        """Effet de dégradé animé"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        t = frame_idx / total_frames * 2 * math.pi
        
        # Dégradé complexe
        for y in range(height):
            for x in range(width):
                r = int(100 + 100 * math.sin(x/100 + y/100 + t))
                g = int(100 + 100 * math.sin(x/80 + y/120 + t + math.pi/2))
                b = int(100 + 100 * math.sin(x/120 + y/80 + t + math.pi))
                frame[y, x] = [b, g, r]
        
        return frame
    
    def create_motivation_effect(self, width, height, frame_idx, total_frames):
        """Effet motivation - couleurs inspirantes"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        t = frame_idx / total_frames * 2 * math.pi
        
        # Couleurs chaudes et inspirantes
        for y in range(height):
            for x in range(width):
                r = int(150 + 80 * math.sin(x/150 + t))
                g = int(100 + 80 * math.sin(y/150 + t))
                b = int(50 + 50 * math.sin((x+y)/200 + t))
                frame[y, x] = [b, g, r]
        
        # Ajouter des éléments lumineux
        for _ in range(10):
            x = random.randint(0, width)
            y = random.randint(0, height)
            cv2.circle(frame, (x, y), 30, (100, 200, 255), -1)
        
        return frame
    
    def create_abstract_effect(self, width, height, frame_idx, total_frames):
        """Effet abstrait - art moderne"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        t = frame_idx / total_frames * 2 * math.pi
        
        # Pattern abstrait
        for i in range(5):
            for j in range(5):
                x = i * width // 5
                y = j * height // 5
                
                color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
                
                if (i + j) % 2 == 0:
                    cv2.rectangle(frame, (x, y), (x + width//5, y + height//5), color, -1)
                else:
                    cv2.circle(frame, (x + width//10, y + height//10), min(width//10, height//10), color, -1)
        
        return frame
    
    def analyze_text_context(self, text):
        """Analyse le contexte du texte pour choisir les bonnes vidéos"""
        # Tokenization et nettoyage
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalpha() and word not in self.stopwords_fr]
        
        # Compter les mots les plus fréquents
        word_freq = Counter(words)
        top_keywords = [word for word, count in word_freq.most_common(10)]
        
        # Déterminer la catégorie principale
        category_keywords = {
            'nature': ['arbre', 'plante', 'fleur', 'forêt', 'mer', 'océan', 'ciel', 'animal'],
            'technologie': ['technologie', 'ordinateur', 'internet', 'digital', 'ai', 'intelligence', 'data'],
            'ville': ['ville', 'bâtiment', 'rue', 'architecture', 'urban', 'métro'],
            'cosmique': ['espace', 'univers', 'étoile', 'planète', 'cosmos', 'galaxie'],
            'motivation': ['succès', 'réussite', 'motivation', 'inspiration', 'objectif', 'but']
        }
        
        best_category = 'abstrait'
        best_score = 0
        
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in top_keywords)
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category, top_keywords
    
    def select_contextual_video(self, category, keywords):
        """Sélectionne une vidéo en fonction du contexte"""
        backgrounds_dir = "assets/backgrounds"
        if not os.path.exists(backgrounds_dir):
            return self.create_color_background()
        
        # Chercher d'abord par catégorie exacte
        category_videos = [f for f in os.listdir(backgrounds_dir) if f.endswith(f'_{category}.mp4')]
        
        if category_videos:
            return os.path.join(backgrounds_dir, random.choice(category_videos))
        
        # Fallback: chercher n'importe quelle vidéo
        all_videos = [f for f in os.listdir(backgrounds_dir) if f.endswith('.mp4')]
        if all_videos:
            return os.path.join(backgrounds_dir, random.choice(all_videos))
        
        # Fallback final: créer une vidéo colorée
        return self.create_color_background()
    
    def text_to_speech(self, text):
        """Convertit le texte en parole avec gestion robuste"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                
                print(f"🎵 Génération de la voix off (tentative {attempt + 1})...")
                
                tts = gtts.gTTS(text=text, lang='fr', slow=False)
                tts.save(temp_path)
                
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    self.audio_path = temp_path
                    print("✓ Voix off générée avec succès")
                    return True
                    
            except Exception as e:
                print(f"✗ Erreur voix off: {e}")
                time.sleep(2)
        
        print("⚠️ Utilisation de l'audio de fallback")
        return self.create_silent_audio(text)
    
    def create_silent_audio(self, text):
        """Crée un audio silencieux de durée proportionnelle au texte"""
        try:
            estimated_duration = max(5, len(text.split()) / 2.5)
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                self.audio_path = tmp_file.name
            
            silent_clip = AudioFileClip.silent(duration=estimated_duration)
            silent_clip.write_audiofile(self.audio_path, fps=22050, verbose=False, logger=None)
            silent_clip.close()
            
            return True
        except Exception as e:
            print(f"✗ Erreur audio silencieux: {e}")
            return False
    
    def generate_subtitles(self, text, audio_duration):
        """Génère des sous-titres parfaitement synchronisés"""
        # Découpage intelligent en phrases
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
        
        total_chars = sum(len(s) for s in sentences)
        char_per_second = total_chars / audio_duration if audio_duration > 0 else 10
        
        self.subtitles = []
        current_time = 0
        
        for sentence in sentences:
            if not sentence:
                continue
                
            duration = max(2.0, len(sentence) / char_per_second)
            end_time = current_time + duration
            
            self.subtitles.append({
                'text': sentence + '.',
                'start': current_time,
                'end': end_time,
                'duration': duration
            })
            
            current_time = end_time + 0.1  # Petit pause entre les phrases
        
        print(f"✓ {len(self.subtitles)} sous-titres générés")
        return self.subtitles
    
    def create_video(self, text, video_style="youtube", duration=30):
        """Crée la vidéo finale avec IA contextuelle"""
        print("🚀 Démarrage de la création de vidéo IA...")
        
        # 1. Analyse contextuelle du texte
        print("🔍 Analyse du contexte...")
        category, keywords = self.analyze_text_context(text)
        print(f"📊 Catégorie détectée: {category}")
        print(f"🔑 Mots-clés: {', '.join(keywords[:5])}")
        
        # 2. Génération de la voix off
        if not self.text_to_speech(text):
            return False
        
        # 3. Obtenir la durée de l'audio
        try:
            audio_clip = AudioFileClip(self.audio_path)
            audio_duration = audio_clip.duration
            audio_clip.close()
        except Exception as e:
            print(f"✗ Erreur audio: {e}")
            return False
        
        # 4. Génération des sous-titres synchronisés
        self.generate_subtitles(text, audio_duration)
        
        # 5. Sélection contextuelle des vidéos d'arrière-plan
        print("🎬 Sélection des séquences vidéo...")
        video_clips = []
        current_duration = 0
        
        while current_duration < audio_duration:
            video_path = self.select_contextual_video(category, keywords)
            
            try:
                clip = VideoFileClip(video_path)
                clip_duration = min(clip.duration, audio_duration - current_duration)
                
                if clip_duration > 0:
                    clip = clip.subclip(0, clip_duration)
                    video_clips.append(clip)
                    current_duration += clip_duration
                
            except Exception as e:
                print(f"⚠️ Erreur vidéo: {e}")
                fallback_clip = ColorClip(size=(1920, 1080), color=(
                    random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                ), duration=min(4, audio_duration - current_duration))
                video_clips.append(fallback_clip)
                current_duration += fallback_clip.duration
        
        # 6. Assemblage final
        if not video_clips:
            print("✗ Aucune séquence vidéo disponible")
            return False
        
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # 7. Ajout de l'audio
        try:
            audio = AudioFileClip(self.audio_path)
            final_video = final_video.set_audio(audio)
        except Exception as e:
            print(f"✗ Erreur ajout audio: {e}")
            return False
        
        # 8. Ajout des sous-titres
        subtitle_clips = []
        for subtitle in self.subtitles:
            try:
                txt_clip = TextClip(
                    subtitle['text'], 
                    fontsize=45, 
                    color='white', 
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=3,
                    size=(final_video.w * 0.85, None),
                    method='caption',
                    align='center'
                )
                txt_clip = txt_clip.set_position(('center', 'center')).set_start(
                    subtitle['start']).set_duration(subtitle['duration'])
                subtitle_clips.append(txt_clip)
            except Exception as e:
                print(f"⚠️ Erreur sous-titre: {e}")
                continue
        
        if subtitle_clips:
            final_video = CompositeVideoClip([final_video] + subtitle_clips)
        
        # 9. Formatage final
        if video_style in ["youtube_short", "tiktok"]:
            final_video = final_video.resize(height=1920)
            final_video = final_video.crop(x_center=final_video.w/2, y_center=final_video.h/2, width=1080, height=1920)
        
        # 10. Export
        try:
            final_video.write_videofile(
                self.output_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                verbose=False,
                logger=None,
                threads=4
            )
            print(f"✅ Vidéo créée: {self.output_path}")
            return True
        except Exception as e:
            print(f"✗ Erreur export: {e}")
            return False
        finally:
            try:
                final_video.close()
                for clip in video_clips:
                    clip.close()
            except:
                pass

def main():
    parser = argparse.ArgumentParser(description="Créateur de vidéos IA avancé")
    parser.add_argument("--text", type=str, help="Texte à transformer en vidéo")
    parser.add_argument("--style", type=str, choices=["youtube", "youtube_short", "tiktok"], 
                       default="youtube", help="Format de la vidéo")
    parser.add_argument("--duration", type=int, default=30, help="Durée approximative")
    parser.add_argument("--output", type=str, help="Chemin de sortie")
    
    args = parser.parse_args()
    
    if not args.text:
        args.text = input("📝 Entrez le texte pour votre vidéo: ")
    
    creator = VideoAICreator()
    
    if args.output:
        creator.output_path = args.output
    
    success = creator.create_video(args.text, args.style, args.duration)
    
    if success:
        print("\n🎉 Création terminée avec succès!")
        print(f"📁 Fichier: {creator.output_path}")
        print(f"⏱️  Durée: {round(AudioFileClip(creator.audio_path).duration, 1)}s")
    else:
        print("❌ Échec de la création")

if __name__ == "__main__":
    main()
