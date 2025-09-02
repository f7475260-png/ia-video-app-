#!/usr/bin/env python3
"""
Installation simplifiée
"""
import os
import subprocess
import sys

def install():
    print("🔧 Installation des dépendances...")
    
    packages = [
        "moviepy==1.0.3",
        "numpy==1.24.3", 
        "Pillow==10.0.0",
        "opencv-python==4.8.1.78"
    ]
    
    for package in packages:
        print(f"📦 Installation de {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ Installation terminée!")
    print("\n🎯 Utilisation:")
    print("python main.py --text \"Votre texte ici\"")
    print("python main.py --text \"Bonjour le monde\" --output ma_video.mp4")

if __name__ == "__main__":
    install()
