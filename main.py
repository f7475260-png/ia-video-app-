import os
import random
import numpy as np
from PIL import Image, ImageDraw
import argparse
import tempfile
import time

print("🎬 Démarrage de Video AI Creator...")

# Configuration simple
WIDTH, HEIGHT = 640, 360
FPS = 24

def create_simple_background(output_path, duration=3):
    """Crée une vidéo simple avec FFmpeg directement"""
    try:
        # Créer une couleur aléatoire
        color = f"{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}"
        
        # Commande FFmpeg pour créer une vidéo colorée
        cmd = f"ffmpeg -f lavfi -i color=c={color}:s={WIDTH}x{HEIGHT}:d={duration} -c:v libx264 {output_path} -y"
        os.system(cmd)
        return True
    except:
        return False

def create_video_with_text(text, output_path):
    """Crée une vidéo simple avec texte"""
    print("📝 Création de la vidéo...")
    
    # Créer un répertoire pour les assets
    os.makedirs("assets", exist_ok=True)
    
    # 1. Créer quelques vidéos d'arrière-plan simples
    backgrounds = []
    for i in range(5):
        bg_path = f"assets/bg_{i}.mp4"
        if create_simple_background(bg_path, duration=5):
            backgrounds.append(bg_path)
            print(f"✅ Vidéo {i+1} créée")
    
    if not backgrounds:
        print("❌ Impossible de créer les backgrounds")
        return False
    
    # 2. Préparer le texte pour les sous-titres
    sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
    if not sentences:
        sentences = [text]
    
    # 3. Créer un fichier de sous-titres
    subtitle_content = ""
    for i, sentence in enumerate(sentences):
        start_time = i * 3
        end_time = (i + 1) * 3
        subtitle_content += f"{i+1}\n"
        subtitle_content += f"00:00:{start_time:02d},000 --> 00:00:{end_time:02d},000\n"
        subtitle_content += f"{sentence}\n\n"
    
    subtitle_path = "assets/subtitles.srt"
    with open(subtitle_path, "w", encoding="utf-8") as f:
        f.write(subtitle_content)
    
    # 4. Sélectionner une vidéo de background
    selected_bg = random.choice(backgrounds)
    
    # 5. Commander FFmpeg pour créer la vidéo finale
    try:
        # Durée estimée basée sur le nombre de phrases
        duration = len(sentences) * 3
        
        # Créer la vidéo avec sous-titres
        cmd = f'ffmpeg -i {selected_bg} -vf "subtitles={subtitle_path}:force_style=\'Fontsize=24,PrimaryColour=&HFFFFFF&\'" -t {duration} -c:a copy {output_path} -y'
        os.system(cmd)
        
        print(f"✅ Vidéo créée avec succès: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Créateur de vidéos simple")
    parser.add_argument("--text", type=str, help="Texte pour la vidéo")
    parser.add_argument("--output", type=str, default="ma_video.mp4", help="Fichier de sortie")
    
    args = parser.parse_args()
    
    if not args.text:
        args.text = "Bienvenue dans votre vidéo générée automatiquement"
    
    print("========================================")
    print("       VIDEO AI CREATOR - SIMPLE        ")
    print("========================================")
    print(f"Texte: {args.text}")
    print(f"Sortie: {args.output}")
    print("========================================")
    
    success = create_video_with_text(args.text, args.output)
    
    if success:
        print("🎉 Félicitations! Votre vidéo est prête!")
        print(f"📁 Fichier: {args.output}")
    else:
        print("😞 La création a échoué")

if __name__ == "__main__":
    main()
