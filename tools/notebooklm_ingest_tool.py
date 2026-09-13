#!/usr/bin/env python3
"""
notebooklm_ingest_tool.py — Autonomous NotebookLM & Gemini Saved Webpage Ingestion Engine
Part of the OSINT & AI Tools Ecosystem.

Automatically scans Downloads for saved NotebookLM / Gemini HTML exports ('Save Page Complete'),
extracts all metadata, source lists, notes, and textual content, updates the master sources index,
and syncs everything into the repo and user profile hubs.
"""

import os
import sys
import glob
import json
import shutil
from pathlib import Path
from html.parser import HTMLParser

DEFAULT_DOWNLOADS_DIR = str(Path.home() / "Downloads")
REPO_NOTEBOOKS_DIR = r"C:\OsintNeoAi\data\chats\notebooks"
MASTER_INDEX_FILE = r"C:\OsintNeoAi\data\notebooklm_master_sources_index.json"
PROFILE_TOOLS_DIR = r"C:\amd949609@gmail.com_Antigravity_CLI_v2.0\tools"


class NotebookHTMLParser(HTMLParser):
    """Extracts raw text, title, and metadata from saved NotebookLM HTML."""
    def __init__(self):
        super().__init__()
        self.texts = []
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.in_script = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.in_script = False

    def handle_data(self, data):
        if not self.in_script:
            d = data.strip()
            if d:
                self.texts.append(d)


def extract_sources_from_text(texts):
    """Extracts individual source titles from parsed text array."""
    sources = []
    capture = False
    for i, t in enumerate(texts):
        if "Chats from Gemini" in t or t == "Sources":
            capture = True
            continue
        if capture:
            if t in ("Chat", "Studio", "Analytics", "Settings", "Share", "Add sources", "Select all"):
                continue
            if "·" in t and any(month in t for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                break
            if len(t) > 2 and t not in ("spark", "arrow_drop_up", "description", "more_vert", "tune", "landscape_2", "add", "dock_to_right"):
                if t not in sources:
                    sources.append(t)
    return sources


def process_notebook_file(html_path, output_dir):
    """Parses a single saved HTML notebook export."""
    html_path = Path(html_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Processing: {html_path.name}")
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_html = f.read()

    parser = NotebookHTMLParser()
    parser.feed(raw_html)
    full_text = "\n".join(parser.texts)

    # Extract Title
    title = html_path.stem.replace(" - Gemini Notebook", "")
    sources = extract_sources_from_text(parser.texts)

    # Save Clean Text
    base_name = html_path.stem.replace(" ", "_").replace("-", "_")
    txt_output_path = output_dir / f"{base_name}_extracted.txt"
    with open(txt_output_path, "w", encoding="utf-8") as out:
        out.write(f"# {title}\n")
        out.write(f"Source File: {html_path.name}\n")
        out.write(f"Total Sources Found: {len(sources)}\n\n")
        out.write("## Sources Catalog:\n")
        for s in sources:
            out.write(f"- {s}\n")
        out.write("\n## Raw Extracted Content:\n")
        out.write(full_text)

    # Copy HTML and companion folder if present
    dest_html = output_dir / html_path.name
    shutil.copy2(html_path, dest_html)
    
    companion_folder = html_path.parent / f"{html_path.stem}_files"
    if companion_folder.exists() and companion_folder.is_dir():
        dest_folder = output_dir / companion_folder.name
        if not dest_folder.exists():
            shutil.copytree(companion_folder, dest_folder)

    metadata = {
        "title": title,
        "filename": html_path.name,
        "total_sources": len(sources),
        "sources": sources,
        "text_length": len(full_text),
        "processed_at": str(Path(html_path).stat().st_mtime)
    }

    print(f"  [✓] Successfully extracted {len(sources)} sources from '{title}'")
    return metadata


def update_master_index(index_file, new_metadata):
    """Updates the centralized JSON index of all ingested notebooks."""
    index_path = Path(index_file)
    data = {"notebooks": {}, "total_ingested": 0}

    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    data["notebooks"][new_metadata["title"]] = new_metadata
    data["total_ingested"] = len(data["notebooks"])

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[+] Master index updated at: {index_path} (Total Notebooks: {data['total_ingested']})")


def scan_and_ingest(downloads_dir=DEFAULT_DOWNLOADS_DIR, target_dir=REPO_NOTEBOOKS_DIR):
    """Scans downloads for any NotebookLM HTML files."""
    print("=" * 65)
    print("  AUTONOMOUS NOTEBOOKLM INGESTION & SOURCE PARSER TOOL")
    print("=" * 65)
    
    patterns = [
        os.path.join(downloads_dir, "*Notebook*.html"),
        os.path.join(downloads_dir, "*Gemini*.html"),
        os.path.join(downloads_dir, "*Osint*.html")
    ]
    
    found_files = set()
    for p in patterns:
        for f in glob.glob(p):
            found_files.add(f)

    if not found_files:
        print(f"[*] No new notebook HTML files found in {downloads_dir}.")
        return

    print(f"[*] Found {len(found_files)} potential notebook files in Downloads.")
    for fpath in found_files:
        meta = process_notebook_file(fpath, target_dir)
        update_master_index(MASTER_INDEX_FILE, meta)

    print("[+] Ingestion run complete.")


if __name__ == "__main__":
    scan_and_ingest()
