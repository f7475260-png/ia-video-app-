import tkinter as tk
from tkinter import ttk

# --- Résolutions selon le format ---
def get_resolution(format_type):
    resolutions = {
        "YouTube": "1920x1080",
        "TikTok": "1080x1920",
        "Short": "1080x1920",
        "Instagram": "1080x1080"
    }
    return resolutions.get(format_type, "1920x1080")

# --- Action lors du changement de format ---
def on_format_change(event):
    selected = format_selector.get()
    res_label.config(text=f"📐 Résolution cible : {get_resolution(selected)}")

# --- Fenêtre principale ---
root = tk.Tk()
root.title("🎬 Sélecteur de Format Vidéo")
root.geometry("420x260")
root.configure(bg="#1e1e2f")

# --- Titre ---
title = tk.Label(
    root,
    text="Choisis ton format de vidéo",
    font=("Helvetica", 16, "bold"),
    bg="#1e1e2f",
    fg="#ffffff"
)
title.pack(pady=20)

# --- Menu déroulant ---
format_selector = ttk.Combobox(
    root,
    values=["YouTube", "TikTok", "Short", "Instagram"],
    font=("Helvetica", 12),
    state="readonly"
)
format_selector.set("YouTube")
format_selector.pack()

# --- Résolution affichée ---
res_label = tk.Label(
    root,
    text=f"📐 Résolution cible : {get_resolution('YouTube')}",
    font=("Helvetica", 12),
    bg="#1e1e2f",
    fg="#f5f5f5"
)
res_label.pack(pady=15)

# --- Bouton de confirmation (optionnel) ---
confirm_btn = tk.Button(
    root,
    text="Valider le format",
    font=("Helvetica", 12),
    bg="#4caf50",
    fg="#ffffff",
    activebackground="#388e3c",
    relief="flat",
    command=lambda: print(f"✅ Format sélectionné : {format_selector.get()} ({get_resolution(format_selector.get())})")
)
confirm_btn.pack(pady=10)

# --- Lier l'action au menu déroulant ---
format_selector.bind("<<ComboboxSelected>>", on_format_change)

# --- Lancer l'interface ---
root.mainloop()
