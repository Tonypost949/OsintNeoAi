import os
import pymupdf
import numpy as np
from PIL import Image
import io
from rapidocr_onnxruntime import RapidOCR

ocr = RapidOCR()
sample_pdf = r"C:\OsintNeoAi\evidence\9b4dd7da-fbac-499b-a44e-520945c7e823.pdf"

doc = pymupdf.open(sample_pdf)
print(f"Total pages in scanned PDF: {len(doc)}")
for pno in range(len(doc)):
    page = doc[pno]
    text = page.get_text()
    if not text.strip():
        # Scanned page - render to pixmap and run OCR
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_np = np.array(img)
        ocr_res, elapse = ocr(img_np)
        if ocr_res:
            lines = [line[1] for line in ocr_res]
            text = "\n".join(lines)
            print(f"Page {pno} (OCR'd {len(lines)} lines in {elapse}s):")
            print(text[:200] + "...\n")
    else:
        print(f"Page {pno} (Native text {len(text)} chars): {text[:200]}...\n")
doc.close()
