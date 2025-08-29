#!/usr/bin/env python3
"""
Script d'installation automatique des dépendances
"""

import os
import sys
import subprocess
import nltk

def install_dependencies():
    print("📦 Installation des dépendances...")
    
    # Installer les packages pip
    requirements = [
        "moviepy==1.0.3",
        "gTTS==2.3.2", 
        "numpy==1.24.3",
        "Pillow==10.0.0",
        "opencv-python==4.8.1.78",
        "nltk==3.8.1"
    ]
    
    for package in requirements:
        subprocess.call([sys.executable, "-m", "pip", "install", package])
    
    # Télécharger les ressources NLTK
    print("📚 Téléchargement des ressources NLTK...")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    
    print("✅ Installation terminée!")
    print("🎯 Lancez: python main.py --text \"Votre texte ici\"")

if __name__ == "__main__":
    install_dependencies()
