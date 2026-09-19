import pytesseract
from PIL import Image
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img_path = Path(r'C:\OsintNeoAi\scratch\lightshot_screenshot.png')
if img_path.exists():
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img)
    print("=== FAST TESSERACT OCR OUTPUT ===")
    print(text)
    out_file = Path(r'C:\OsintNeoAi\evidence\jetbrains_toolbox_screenshot_ocr.md')
    out_file.write_text("# 🖼️ JETBRAINS TOOLBOX SCREENSHOT OCR TRANSCRIPT\n\n```text\n" + text + "\n```", encoding='utf-8')
    print(f"✓ Saved to: {out_file}")
else:
    print("Screenshot file missing!")
