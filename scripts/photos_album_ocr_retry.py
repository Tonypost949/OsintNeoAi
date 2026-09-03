import sys
import time
from pathlib import Path
from PIL import Image

BASE = Path(r'C:\Users\AMD949~1\AppData\Local\Temp\opencode\photos_a74G5sEDR54YwTiF7')
DL = BASE / 'downloads'
OCR = BASE / 'ocr'

import easyocr
import cv2
import numpy as np

def load_ok(fp):
    img = cv2.imread(str(fp))
    if img is None:
        return None
    h, w = img.shape[:2]
    if h == 0 or w == 0:
        return None
    # downscale to max 2000 px to avoid resize assertion and speed up
    maxd = 2000
    scale = min(1.0, maxd / max(h, w))
    if scale < 1.0:
        img = cv2.resize(img, (int(w*scale), int(h*scale)))
    return img

def main():
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    targets = ['photo_010', 'photo_017', 'photo_021', 'photo_023']
    for name in targets:
        out = OCR / f'{name}.txt'
        fp = DL / f'{name}.jpg'
        img = load_ok(fp)
        if img is None:
            out.write_text('[EMPTY/INVALID IMAGE]', encoding='utf-8')
            print(f'{name}: invalid', flush=True)
            continue
        t0 = time.time()
        results = reader.readtext(img, detail=0, paragraph=True)
        text = '\n'.join(results)
        out.write_text(text, encoding='utf-8')
        print(f'{name}: chars={len(text)} {time.time()-t0:.1f}s', flush=True)

if __name__ == '__main__':
    main()
