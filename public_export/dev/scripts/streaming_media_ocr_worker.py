import os
import sys
import io
import time
import zipfile
import json
import glob

BASE_DIR = r"C:\OsintNeoAi\data\takeouts\etp949609_takeout_20260913"
OCR_DIR = os.path.join(BASE_DIR, "OCR_Extracted_Text")
METAMEDIA_DIR = os.path.join(BASE_DIR, "metamedia")
DOWNLOADS_DIR = os.path.expanduser(r"~\Downloads")

os.makedirs(OCR_DIR, exist_ok=True)
os.makedirs(METAMEDIA_DIR, exist_ok=True)

def init_ocr_engine():
    try:
        import easyocr
        print("[OCR ENGINE] Loading EasyOCR neural model into memory...")
        reader = easyocr.Reader(['en'], gpu=False)
        print("[✓] EasyOCR neural reader loaded successfully!")
        return reader
    except Exception as e:
        print(f"[OCR ENGINE ERROR] Could not load EasyOCR: {e}")
        return None

def process_image_bytes(reader, img_bytes, img_name):
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(img_bytes))
        
        # Extract EXIF if available
        exif_data = {}
        try:
            info = img._getexif()
            if info:
                for tag, val in info.items():
                    exif_data[str(tag)] = str(val)[:100]
        except Exception:
            pass
            
        # Run EasyOCR on the image bytes
        ocr_results = []
        full_text = ""
        if reader:
            res = reader.readtext(img_bytes)
            for bbox, text, conf in res:
                ocr_results.append({
                    "text": text,
                    "confidence": float(conf)
                })
            full_text = "\n".join([r["text"] for r in ocr_results])
            
        # Save OCR transcript if text was detected
        if full_text.strip():
            txt_path = os.path.join(OCR_DIR, f"{img_name}.ocr.txt")
            with open(txt_path, "w", encoding="utf-8") as fp:
                fp.write(f"IMAGE_SOURCE: {img_name}\n")
                fp.write(f"OCR_ENGINE: EasyOCR Neural\n")
                fp.write(f"EXTRACTED_AT: {time.time()}\n")
                fp.write("="*60 + "\n\n")
                fp.write(full_text)
            print(f"  [★ OCR HIT] Extracted text from {img_name} ({len(ocr_results)} text lines)")
            
        # Save metadata record in metamedia/
        meta_record = {
            "image_filename": img_name,
            "dimensions": f"{img.width}x{img.height}",
            "format": img.format,
            "has_exif": bool(exif_data),
            "ocr_text_length": len(full_text),
            "ocr_snippets": [r["text"] for r in ocr_results[:5]]
        }
        meta_path = os.path.join(METAMEDIA_DIR, f"{img_name}.meta.json")
        with open(meta_path, "w", encoding="utf-8") as fp:
            json.dump(meta_record, fp, indent=2)
            
    except Exception as e:
        print(f"  [ERROR] Processing {img_name}: {e}")

def run_streaming_media_ocr():
    reader = init_ocr_engine()
    
    print("\n[STREAMER] Scanning for Takeout zip archives to run neural OCR on pictures...")
    
    # 1. Look for existing zip files in Downloads
    zip_files = glob.glob(os.path.join(DOWNLOADS_DIR, "takeout-*.zip"))
    print(f"Found {len(zip_files)} Takeout zip archives in Downloads.")
    
    img_exts = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.heic']
    
    for zpath in zip_files:
        print(f"\n[SCANNING ARCHIVE] {os.path.basename(zpath)}...")
        try:
            with zipfile.ZipFile(zpath, 'r') as zf:
                for item in zf.namelist():
                    lower = item.lower()
                    if any(lower.endswith(ext) for ext in img_exts):
                        img_name = os.path.basename(item)
                        # Check if already processed
                        meta_check = os.path.join(METAMEDIA_DIR, f"{img_name}.meta.json")
                        if not os.path.exists(meta_check):
                            print(f"[OCR SCAN] Reading picture pixels: {img_name}...")
                            img_data = zf.read(item)
                            process_image_bytes(reader, img_data, img_name)
        except Exception as e:
            print(f"[ERROR] Reading archive {zpath}: {e}")
            
    print("\n[✓] STREAMING MEDIA OCR PASS COMPLETED!")

if __name__ == "__main__":
    run_streaming_media_ocr()
