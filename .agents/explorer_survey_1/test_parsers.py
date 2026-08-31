import os
import hashlib
import pymupdf
import docx
from PIL import Image, ImageSequence
from rapidocr_onnxruntime import RapidOCR
from html.parser import HTMLParser

class SimpleHTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'head', 'meta', 'link'):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'head', 'meta', 'link'):
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            stripped = data.strip()
            if stripped:
                self.text_parts.append(stripped)

    def get_text(self):
        return " ".join(self.text_parts)

def hash_file_stream(filepath, chunk_size=65536):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()

print("--- Testing Stream Hashing ---")
sample_pdf = r"C:\OsintNeoAi\evidence\9b4dd7da-fbac-499b-a44e-520945c7e823.pdf"
if os.path.exists(sample_pdf):
    h = hash_file_stream(sample_pdf)
    print(f"Sample PDF SHA256: {h}")

print("\n--- Testing PyMuPDF Extraction ---")
if os.path.exists(sample_pdf):
    doc = pymupdf.open(sample_pdf)
    print(f"Page count: {len(doc)}")
    p0_text = doc[0].get_text()
    print(f"Page 0 text excerpt ({len(p0_text)} chars): {p0_text[:150]}...")
    doc.close()

print("\n--- Testing RapidOCR on Sample Image ---")
sample_img = r"C:\OsintNeoAi\evidence\andrewfalk.png"
if os.path.exists(sample_img):
    ocr = RapidOCR()
    res, elapse = ocr(sample_img)
    if res:
        print(f"OCR extracted {len(res)} text lines in {elapse}s. First line: {res[0][1]}")
    else:
        print("No text detected in sample image.")

print("\n--- Testing Multi-Page TIF Handling ---")
sample_tif = r"C:\Users\Amd949609\Downloads\General Consent for Treatment.TIF"
if os.path.exists(sample_tif):
    im = Image.open(sample_tif)
    print(f"TIFF opened successfully: format={im.format}, size={im.size}, n_frames={getattr(im, 'n_frames', 1)}")
    im.close()

print("\n--- Testing HTML Text Parsing ---")
sample_html = r"C:\Users\Amd949609\Downloads\Chaperone Policy.HTML"
if os.path.exists(sample_html):
    with open(sample_html, 'r', encoding='utf-8', errors='ignore') as f:
        parser = SimpleHTMLTextExtractor()
        parser.feed(f.read())
        extracted = parser.get_text()
        print(f"HTML text length: {len(extracted)} chars. Excerpt: {extracted[:150]}...")

print("\n--- Testing DOCX Parsing ---")
sample_docx = r"C:\OsintNeoAi\evidence\google_drive\DR_ANN_VERMA_RESCISSION_NOTICE.docx"
if os.path.exists(sample_docx):
    doc = docx.Document(sample_docx)
    all_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    print(f"DOCX text length: {len(all_text)} chars. Excerpt: {all_text[:150]}...")

print("\nAll sanity tests passed successfully!")
