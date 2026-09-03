import sys
import time
from pathlib import Path

BASE = Path(r'C:\Users\AMD949~1\AppData\Local\Temp\opencode\photos_a74G5sEDR54YwTiF7')
DL = BASE / 'downloads'
OCR = BASE / 'ocr'
OCR.mkdir(parents=True, exist_ok=True)

import easyocr

def main():
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    files = sorted(DL.glob('*.jpg'))
    print(f'OCR {len(files)} images', flush=True)
    for i, fp in enumerate(files, 1):
        out = OCR / f'{fp.stem}.txt'
        if out.exists() and out.stat().st_size > 0:
            print(f'[{i}/{len(files)}] {fp.name} cached', flush=True)
            continue
        t0 = time.time()
        try:
            results = reader.readtext(str(fp), detail=0, paragraph=True)
            text = '\n'.join(results)
        except Exception as e:
            text = f'[OCR ERROR] {e}'
        out.write_text(text, encoding='utf-8')
        nchars = len(text)
        print(f'[{i}/{len(files)}] {fp.name} chars={nchars} {time.time()-t0:.1f}s', flush=True)

if __name__ == '__main__':
    main()
