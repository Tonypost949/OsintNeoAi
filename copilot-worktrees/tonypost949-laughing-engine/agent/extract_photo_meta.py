from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os

artifact_dir = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7"
images = [
    "media__1781675398620.png",
    "media__1781675541095.png",
    "media__1781718939114.png"
]

def get_exif_data(image_path):
    ret = {}
    try:
        image = Image.open(image_path)
        if hasattr(image, '_getexif'):
            exif_info = image._getexif()
            if exif_info is not None:
                for tag, value in exif_info.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
        
        # Also try info dict for PNGs
        if not ret and 'exif' in image.info:
            print(f"Found raw EXIF data in info for {image_path}")
            
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
    return ret

for img in images:
    path = os.path.join(artifact_dir, img)
    print(f"\n--- Metadata for {img} ---")
    data = get_exif_data(path)
    if data:
        for k, v in data.items():
            if isinstance(v, bytes):
                print(f"{k}: <bytes>")
            else:
                print(f"{k}: {v}")
    else:
        print("No EXIF data found.")
