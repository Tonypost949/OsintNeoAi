import os
import sys
import json
from pathlib import Path

def main():
    print("=== HIGH-ACCURACY EASYOCR & TESSERACT FULL ALBUM SCANNER ===")
    img_dir = Path(r'C:\OsintNeoAi\scratch\album_W6cAZwiDkZQtkMKr7')
    images = sorted(list(img_dir.glob('*.jpg')))
    print(f"Total downloaded photos queued for OCR: {len(images)}")
    out_file = Path(r'C:\OsintNeoAi\evidence\album_W6cAZwiDkZQtkMKr7_full_ocr_index.md')
    print(f"Destination index file: {out_file}")

if __name__ == '__main__':
    main()
