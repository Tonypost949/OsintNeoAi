import easyocr
from pathlib import Path

img_path = Path(r'C:\OsintNeoAi\scratch\lightshot_screenshot.png')
print(f"Reading image: {img_path} (exists: {img_path.exists()})")

reader = easyocr.Reader(['en'], gpu=False)
results = reader.readtext(str(img_path))

lines = [res[1] for res in results if res[2] > 0.2]

print("\n=== SCREENSHOT OCR RESULTS ===")
for l in lines:
    print(" -", l)

out_file = Path(r'C:\OsintNeoAi\evidence\jetbrains_toolbox_screenshot_ocr.md')
out_file.write_text("# 🖼️ JETBRAINS TOOLBOX SCREENSHOT TRANSCRIPT\n\n" + "\n".join(f"- `{l}`" for l in lines), encoding='utf-8')
print("\n✓ Saved to:", out_file)
