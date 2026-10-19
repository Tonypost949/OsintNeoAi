#!/usr/bin/env python3
"""
extract_notebooks.py — Local Notebook Text Extractor & Rclone Sync
Scans C:\\OsintNeoAi\\data\\chats\\notebooks for saved HTML exports, strips HTML tags,
extracts clean readable text, and syncs to Google Drive via rclone.
"""

import os
import shutil
import subprocess
from pathlib import Path
from html.parser import HTMLParser

# ==========================================
# Configuration for Local Saved Notebooks
# ==========================================
NOTEBOOKS_DIR = r"C:\OsintNeoAi\data\chats\notebooks"
OUTPUT_DIR = r"C:\OsintNeoAi\data\filtered_chats"
RCLONE_DESTINATION = "gdrive:Sharedall/Gemini_Exports"
# ==========================================


class StandardHTMLTextExtractor(HTMLParser):
    """Zero-dependency HTML text extractor using standard library."""
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


def extract_text_from_html(file_path, output_dir):
    """Parses saved HTML notebooks and extracts the conversation text."""
    filename = os.path.basename(file_path)
    text_filename = filename.replace(".html", "_clean.txt")
    output_path = os.path.join(output_dir, text_filename)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Extracting text from: {filename}...")
    try:
        # Try BeautifulSoup if available, fallback to built-in HTMLParser
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
        except ImportError:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_html = f.read()
            parser = StandardHTMLTextExtractor()
            parser.feed(raw_html)
            text = '\n'.join(parser.texts)

        # Save the clean text
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write(text)
            
        print(f"  -> Saved clean text to {text_filename} ({len(text)} chars)")
        return True
    except Exception as e:
        print(f"  -> Error processing {filename}: {e}")
        return False


def process_notebooks_and_upload():
    print("--- Starting Local Notebook Extraction ---")
    notebooks_path = Path(NOTEBOOKS_DIR)
    processed_count = 0

    if not notebooks_path.exists():
        print(f"[!] Directory not found: {NOTEBOOKS_DIR}")
        return

    # 1. Find all saved .html files in your notebooks directory (excluding companion folders)
    for root, _, files in os.walk(notebooks_path):
        for filename in files:
            if filename.endswith(".html") and not filename.endswith("RotateCookiesPage.html") and not filename.endswith("app.html"):
                file_path = os.path.join(root, filename)
                
                # 2. Extract the text
                if extract_text_from_html(file_path, OUTPUT_DIR):
                    processed_count += 1
    
    print(f"[+] Finished extracting {processed_count} notebook files.")

    # 3. Upload the clean text to Drive via rclone
    if processed_count > 0:
        print(f"[*] Starting rclone sync to {RCLONE_DESTINATION}...")
        command = ["rclone", "copy", OUTPUT_DIR, RCLONE_DESTINATION, "--progress"]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                print("[+] Rclone upload complete!")
            else:
                print(f"[!] Rclone notification (exit {result.returncode}): {result.stderr or result.stdout}")
        except FileNotFoundError:
            print("[!] 'rclone' not found on PATH. Files remain safely saved locally in filtered_chats.")
        except Exception as e:
            print(f"[!] Rclone upload exception: {e}")


if __name__ == "__main__":
    process_notebooks_and_upload()
