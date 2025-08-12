# utils/asset_manager.py
from __future__ import annotations
import os, sys, re, json, time, argparse, shutil, mimetypes
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from datetime import timedelta

VOICE_EXT = {".mp3", ".wav", ".m4a", ".aac", ".ogg"}
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm"}
SUB_EXT   = {".srt", ".vtt", ".txt"}

ASSETS = {
    "voices": Path("assets/voices"),
    "videos": Path("assets/videos"),
    "subtitles": Path("assets/subtitles"),
}

def ensure_dirs():
    for p in ASSETS.values():
        p.mkdir(parents=True, exist_ok=True)

def sanitize_filename(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]+", "-", name.strip())
    name = re.sub(r"\s+", " ", name)
    return name[:200] or f"file-{int(time.time())}"

def unique_path(dst: Path) -> Path:
    if not dst.exists():
        return dst
    stem, suffix = dst.stem, dst.suffix
    i = 1
    while True:
        candidate = dst.with_name(f"{stem}-{i}{suffix}")
        if not candidate.exists():
            return candidate
        i += 1

def guess_downloads_dir() -> Path:
    home = Path.home()
    candidates = [
        home / "Downloads",                              # Linux/Mac
        home / "Téléchargements",                        # FR Windows
        home / "Descargas", home / "Download",           # variations
    ]
    for c in candidates:
        if c.exists():
            return c
    return home  # fallback

def download_file(url: str, dest_dir: Path, name_hint: str | None = None) -> Path:
    ensure_dirs()
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=60) as resp:
            data = resp.read()
            ct = resp.headers.get("Content-Type", "")
            ext = mimetypes.guess_extension(ct.split(";")[0].strip()) or ""
            if not ext or ext == ".bin":
                # Try from URL
                parsed = Path(url.split("?")[0]).suffix.lower()
                if parsed in VOICE_EXT | VIDEO_EXT | SUB_EXT:
                    ext = parsed
            base = sanitize_filename(name_hint or Path(url.split("?")[0]).stem)
            dest = unique_path(dest_dir / f"{base}{ext}")
            with open(dest, "wb") as f:
                f.write(data)
            return dest
    except (HTTPError, URLError) as e:
        raise RuntimeError(f"Échec téléchargement {url}: {e.reason if hasattr(e,'reason') else e}") from e

def move_if_match(src: Path, exts: set[str], dest_dir: Path) -> list[Path]:
    moved = []
    if src.suffix.lower() in exts:
        ensure_dirs()
        dest = unique_path(dest_dir / sanitize_filename(src.name))
        shutil.move(str(src), str(dest))
        moved.append(dest)
    return moved

def convert_vtt_to_srt(vtt_path: Path) -> Path:
    srt_path = vtt_path.with_suffix(".srt")
    with open(vtt_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    out = []
    idx = 1
    for line in lines:
        # Skip WEBVTT header and NOTE blocks
        if line.strip().upper().startswith("WEBVTT") or line.strip().upper().startswith("NOTE"):
            continue
        # Convert time format 00:00:01.000 --> 00:00:01,000
        if "-->" in line:
            line = line.replace(".", ",", 1)  # replace first dot in start time
            arrow = line.find("-->")
            after = line[arrow+3:]
            if "." in after:
                firstdot = after.find(".")
                after = after[:firstdot] + "," + after[firstdot+1:]
                line = line[:arrow+3] + after
            out.append(f"{idx}\n")
            idx += 1
            out.append(line)
        elif line.strip() == "":
            out.append("\n")
        else:
            out.append(line)
    with open(srt_path, "w", encoding="utf-8") as f:
        f.writelines(out)
    return srt_path

def txt_to_srt(txt_path: Path, duration_per_line: float = 3.0) -> Path:
    srt_path = txt_path.with_suffix(".srt")
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip()]
    def fmt(t):
        td = timedelta(seconds=t)
        h, rem = divmod(td.seconds, 3600)
        m, s = divmod(rem, 60)
        ms = int(td.microseconds / 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    t = 0.0
    blocks = []
    for i, text in enumerate(lines, 1):
        start = fmt(t)
        end = fmt(t + duration_per_line)
        blocks.append(f"{i}\n{start} --> {end}\n{text}\n\n")
        t += duration_per_line
    with open(srt_path, "w", encoding="utf-8") as f:
        f.writelines(blocks)
    return srt_path

def process_manifest(manifest_path: Path) -> dict[str, list[Path]]:
    if not manifest_path.exists():
        return {"voices": [], "videos": [], "subtitles": []}
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    results = {"voices": [], "videos": [], "subtitles": []}
    for item in manifest.get("voices", []):
        p = download_file(item["url"], ASSETS["voices"], item.get("name"))
        results["voices"].append(p)
    for item in manifest.get("videos", []):
        p = download_file(item["url"], ASSETS["videos"], item.get("name"))
        results["videos"].append(p)
    for item in manifest.get("subtitles", []):
        p = download_file(item["url"], ASSETS["subtitles"], item.get("name"))
        # auto-convert vtt -> srt
        if p.suffix.lower() == ".vtt":
            p = convert_vtt_to_srt(p)
        results["subtitles"].append(p)
    return results

def pull_from_downloads(downloads_dir: Path) -> dict[str, list[Path]]:
    results = {"voices": [], "videos": [], "subtitles": []}
    for src in downloads_dir.glob("*"):
        if not src.is_file():
            continue
        low = src.suffix.lower()
        if low in VOICE_EXT:
            results["voices"] += move_if_match(src, VOICE_EXT, ASSETS["voices"])
        elif low in VIDEO_EXT:
            results["videos"] += move_if_match(src, VIDEO_EXT, ASSETS["videos"])
        elif low in SUB_EXT:
            # move first
            moved = move_if_match(src, SUB_EXT, ASSETS["subtitles"])
            for p in moved:
                if p.suffix.lower() == ".vtt":
                    srt = convert_vtt_to_srt(p)
                    try:
                        p.unlink(missing_ok=True)
                    except Exception:
                        pass
                    results["subtitles"].append(srt)
                elif p.suffix.lower() == ".txt":
                    srt = txt_to_srt(p)
                    results["subtitles"].append(srt)
                else:
                    results["subtitles"].append(p)
    return results

def run(manifest: Path | None, from_downloads: bool) -> dict[str, list[Path]]:
    ensure_dirs()
    summary = {"voices": [], "videos": [], "subtitles": []}
    if manifest:
        r = process_manifest(manifest)
        for k in summary:
            summary[k] += r[k]
    if from_downloads:
        ddir = guess_downloads_dir()
        r = pull_from_downloads(ddir)
        for k in summary:
            summary[k] += r[k]
    return summary

def print_summary(summary: dict[str, list[Path]]):
    def fmt(items): return "\n  - " + "\n  - ".join(map(str, items)) if items else " (aucun)"
    print("Voix:", fmt(summary["voices"]))
    print("Vidéos:", fmt(summary["videos"]))
    print("Sous-titres:", fmt(summary["subtitles"]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gestion automatique des assets (voix, vidéos, sous-titres).")
    parser.add_argument("--manifest", type=str, default="assets_manifest.json", help="Fichier JSON d'URLs à télécharger.")
    parser.add_argument("--no-manifest", action="store_true", help="Ignorer le manifest même s'il existe.")
    parser.add_argument("--from-downloads", action="store_true", help="Importer depuis le dossier Téléchargements.")
    args = parser.parse_args()

    manifest_path = None if args.no_manifest else Path(args.manifest)
    summary = run(manifest_path, from_downloads=args.from_downloads)
    print_summary(summary)
