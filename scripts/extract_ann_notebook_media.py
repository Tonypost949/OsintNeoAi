"""
extract_ann_notebook_media.py
Extract and download ALL media, audio, PDFs, Drive files, and images
from the ann Gemini Notebook HTML into C:\brainmedus_Antigravity\
"""

import re, os, json, shutil, requests
from pathlib import Path
from urllib.parse import urlparse, unquote

HTML_PATH   = r"C:\Users\Amd949609\Downloads\ann Gemini Notebook.html"
FILES_DIR   = r"C:\Users\Amd949609\Downloads\ann Gemini Notebook_files"
DEST_ROOT   = r"C:\brainmedus_Antigravity\docs\notebooks"
MEDIA_DIR   = os.path.join(DEST_ROOT, "media")
AUDIO_DIR   = os.path.join(DEST_ROOT, "audio")
IMAGES_DIR  = os.path.join(DEST_ROOT, "images")
DOCS_DIR    = os.path.join(DEST_ROOT, "source_docs")

for d in [MEDIA_DIR, AUDIO_DIR, IMAGES_DIR, DOCS_DIR]:
    os.makedirs(d, exist_ok=True)

print("=" * 65)
print("  ANN GEMINI NOTEBOOK — FULL MEDIA EXTRACTION")
print("=" * 65)

with open(HTML_PATH, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

# ── 1. Audio URLs ──────────────────────────────────────────────────
audio_patterns = [
    r'https?://[^\s"\'<>]+\.(?:mp3|mp4|m4a|ogg|wav|aac)[^\s"\'<>]*',
    r'https?://[^\s"\'<>]*(?:audio|podcast|overview)[^\s"\'<>]*\.(?:mp3|mp4|m4a)',
    r'"(https?://[^\s"\'<>]+(?:audio|sound|mp3|m4a)[^\s"\'<>]*)"',
    r'src="(https?://[^"]+)"[^>]*type="audio',
]
audio_urls = set()
for pat in audio_patterns:
    audio_urls.update(re.findall(pat, html, re.I))
print(f"\n[AUDIO] Found {len(audio_urls)} audio URLs")
for u in audio_urls:
    print(f"  >> {u[:100]}")

# ── 2. Google Drive / Docs / Sheets links ─────────────────────────
drive_urls = set(re.findall(
    r'https?://(?:drive|docs|sheets|slides)\.google\.com/[^\s"\'<>]+', html, re.I))
print(f"\n[DRIVE] Found {len(drive_urls)} Google Drive/Docs URLs")
for u in sorted(drive_urls):
    print(f"  >> {u[:100]}")

# ── 3. Direct PDF links ───────────────────────────────────────────
pdf_urls = set(re.findall(
    r'https?://[^\s"\'<>]+\.pdf[^\s"\'<>]*', html, re.I))
print(f"\n[PDFs] Found {len(pdf_urls)} PDF URLs")
for u in sorted(pdf_urls):
    print(f"  >> {u[:100]}")

# ── 4. NotebookLM artifact URLs ───────────────────────────────────
nb_urls = set(re.findall(
    r'https?://notebooklm\.google\.com/[^\s"\'<>]+', html, re.I))
print(f"\n[NOTEBOOKLM] Found {len(nb_urls)} artifact URLs")
for u in sorted(nb_urls):
    print(f"  >> {u[:100]}")

# ── 5. GCS / googleapis media ─────────────────────────────────────
gcs_urls = set(re.findall(
    r'https?://(?:storage\.googleapis\.com|lh3\.googleusercontent\.com|uc\.googledrive\.com)[^\s"\'<>]+',
    html, re.I))
print(f"\n[GCS] Found {len(gcs_urls)} googleapis media URLs")

# ── 6. Copy ALL files from _files companion folder ────────────────
print(f"\n[FILES] Copying all companion _files to brainmedus...")
files_src = Path(FILES_DIR)
copied = 0
if files_src.exists():
    for item in files_src.iterdir():
        if item.is_file():
            name = item.name
            # Route by extension/type
            if any(name.lower().endswith(x) for x in ['.jpg','.jpeg','.png','.gif','.webp','.svg']):
                dest = Path(IMAGES_DIR) / name
            elif any(name.lower().endswith(x) for x in ['.mp3','.mp4','.m4a','.ogg','.wav']):
                dest = Path(AUDIO_DIR) / name
            elif any(name.lower().endswith(x) for x in ['.pdf','.docx','.xlsx','.pptx']):
                dest = Path(DOCS_DIR) / name
            else:
                dest = Path(MEDIA_DIR) / name
            shutil.copy2(item, dest)
            print(f"  [+] Copied: {name} ({round(item.stat().st_size/1024,1)} KB) → {dest.parent.name}/")
            copied += 1

print(f"\n[FILES] {copied} files copied from _files companion folder")

# ── 7. Try to download audio if URLs found ────────────────────────
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
dl_count = 0
if audio_urls:
    print(f"\n[DOWNLOAD] Attempting to fetch {len(audio_urls)} audio files...")
    for url in audio_urls:
        try:
            fname = unquote(urlparse(url).path.split("/")[-1]) or "audio_overview.mp3"
            if not any(fname.endswith(x) for x in ['.mp3','.mp4','.m4a','.ogg']):
                fname += ".mp3"
            dest = Path(AUDIO_DIR) / fname
            r = requests.get(url, headers=headers, stream=True, timeout=30)
            if r.status_code == 200:
                with open(dest, "wb") as out:
                    for chunk in r.iter_content(8192):
                        out.write(chunk)
                size = dest.stat().st_size
                print(f"  [✓] Downloaded: {fname} ({round(size/1024/1024,2)} MB)")
                dl_count += 1
            else:
                print(f"  [!] HTTP {r.status_code} — needs auth: {url[:80]}")
        except Exception as e:
            print(f"  [!] Error: {e}")

# ── 8. Save full URL manifest ─────────────────────────────────────
manifest = {
    "notebook": "ann Gemini Notebook",
    "account": "brainmedus@gmail.com",
    "audio_urls": list(audio_urls),
    "drive_urls": list(drive_urls),
    "pdf_urls": list(pdf_urls),
    "notebooklm_urls": list(nb_urls),
    "gcs_urls": list(gcs_urls),
    "files_copied": copied,
    "audio_downloaded": dl_count
}
manifest_path = os.path.join(DEST_ROOT, "ann_notebook_media_manifest.json")
with open(manifest_path, "w") as mf:
    json.dump(manifest, mf, indent=2)

print(f"\n[✓] Manifest saved: {manifest_path}")
print(f"\n{'='*65}")
print(f"  SUMMARY")
print(f"{'='*65}")
print(f"  Files copied from _files:   {copied}")
print(f"  Audio downloaded:           {dl_count}")
print(f"  Drive URLs found:           {len(drive_urls)}")
print(f"  NotebookLM artifact URLs:   {len(nb_urls)}")
print(f"  Dest: {DEST_ROOT}")
print(f"{'='*65}")
