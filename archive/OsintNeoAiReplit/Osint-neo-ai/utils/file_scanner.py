import os
import json
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path

# Optional metadata extractors
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import mutagen
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

SUPPORTED_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic"],
    "document": [".pdf", ".doc", ".docx", ".txt", ".csv", ".xlsx", ".xls", ".odt"],
    "audio": [".mp3", ".mp4", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "video": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".3gp"],
    "contact": [".vcf", ".vcard"],
    "data": [".json", ".xml", ".yaml", ".yml", ".db", ".sqlite"],
}

def get_file_category(ext):
    ext = ext.lower()
    for category, exts in SUPPORTED_EXTENSIONS.items():
        if ext in exts:
            return category
    return "other"

def get_file_hash(filepath, chunk_size=8192):
    try:
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "N/A"

def extract_image_metadata(filepath):
    meta = {}
    if not PIL_AVAILABLE:
        return {"note": "PIL not available for EXIF extraction"}
    try:
        with Image.open(filepath) as img:
            meta["format"] = img.format
            meta["mode"] = img.mode
            meta["width"] = img.size[0]
            meta["height"] = img.size[1]
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        continue
                    if tag in ["GPSInfo", "Make", "Model", "DateTime", "Software",
                               "Artist", "Copyright", "ImageDescription", "UserComment"]:
                        meta[str(tag)] = str(value)[:200]
    except Exception as e:
        meta["error"] = str(e)
    return meta

def extract_audio_metadata(filepath):
    meta = {}
    if not MUTAGEN_AVAILABLE:
        return {"note": "mutagen not available"}
    try:
        audio = mutagen.File(filepath)
        if audio:
            for key in ["TIT2", "TPE1", "TALB", "TDRC", "TCON", "title", "artist", "album", "date", "genre"]:
                if key in audio:
                    meta[key] = str(audio[key])
            if hasattr(audio, "info"):
                meta["duration_sec"] = round(audio.info.length, 1) if hasattr(audio.info, "length") else "N/A"
                meta["bitrate"] = getattr(audio.info, "bitrate", "N/A")
    except Exception as e:
        meta["error"] = str(e)
    return meta

def extract_text_preview(filepath, max_chars=500):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_chars)
        return {"preview": content.replace("\n", " ").strip()}
    except Exception:
        return {}

def extract_vcf_metadata(filepath):
    meta = {}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        lines = content.splitlines()
        for line in lines:
            if line.startswith("FN:"):
                meta["full_name"] = line[3:].strip()
            elif line.startswith("TEL"):
                meta.setdefault("phones", []).append(line.split(":")[-1].strip())
            elif line.startswith("EMAIL"):
                meta.setdefault("emails", []).append(line.split(":")[-1].strip())
            elif line.startswith("ADR"):
                meta["address"] = line.split(":")[-1].strip()
            elif line.startswith("ORG:"):
                meta["org"] = line[4:].strip()
        if "phones" in meta:
            meta["phones"] = ", ".join(meta["phones"][:5])
        if "emails" in meta:
            meta["emails"] = ", ".join(meta["emails"][:5])
    except Exception as e:
        meta["error"] = str(e)
    return meta

def scan_file(filepath):
    path = Path(filepath)
    if not path.exists() or not path.is_file():
        return None
    ext = path.suffix.lower()
    category = get_file_category(ext)
    try:
        stat = path.stat()
        file_size = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        file_size = 0
        modified = "N/A"
        created = "N/A"

    metadata = {
        "filename": path.name,
        "extension": ext,
        "category": category,
        "size_bytes": file_size,
        "modified": modified,
        "created": created,
        "md5": get_file_hash(filepath),
    }

    if category == "image":
        metadata.update(extract_image_metadata(filepath))
    elif category == "audio":
        metadata.update(extract_audio_metadata(filepath))
    elif category in ["document", "data"] and ext in [".txt", ".csv", ".json", ".xml", ".yaml", ".yml"]:
        metadata.update(extract_text_preview(filepath))
    elif category == "contact":
        metadata.update(extract_vcf_metadata(filepath))

    return {
        "file_path": str(filepath),
        "file_type": category,
        "file_size": file_size,
        "metadata": metadata,
    }

def scan_directory(directory, max_files=500, progress_callback=None):
    results = []
    errors = []
    count = 0

    all_files = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden system dirs
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "node_modules"]]
        for fname in files:
            if not fname.startswith("."):
                all_files.append(os.path.join(root, fname))
            if len(all_files) >= max_files:
                break
        if len(all_files) >= max_files:
            break

    total = len(all_files)
    for i, filepath in enumerate(all_files):
        try:
            result = scan_file(filepath)
            if result:
                results.append(result)
        except Exception as e:
            errors.append({"file": filepath, "error": str(e)})
        count += 1
        if progress_callback:
            progress_callback(count, total)

    return results, errors

def get_directory_summary(results):
    summary = {
        "total_files": len(results),
        "total_size_bytes": sum(r["file_size"] for r in results),
        "by_category": {},
        "notable_finds": [],
    }
    for r in results:
        cat = r["file_type"]
        summary["by_category"][cat] = summary["by_category"].get(cat, 0) + 1

        # Flag notable findings
        meta = r.get("metadata", {})
        if "GPSInfo" in meta or "GPS" in str(meta):
            summary["notable_finds"].append(f"GPS data found: {r['file_path']}")
        if cat == "contact":
            summary["notable_finds"].append(f"Contact file: {r['file_path']} — {meta.get('full_name', 'Unknown')}")
        if r["file_size"] > 100 * 1024 * 1024:
            summary["notable_finds"].append(f"Large file (>100MB): {r['file_path']}")

    summary["total_size_mb"] = round(summary["total_size_bytes"] / (1024 * 1024), 2)
    return summary
