import os
import uuid

def save_upload(file) -> str:
    os.makedirs("assets/videos", exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    file_path = f"assets/videos/{uuid.uuid4()}{ext}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path
