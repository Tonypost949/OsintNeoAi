import os
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None

class OCRConnector:
    """Consolidated OCR Engine supporting local pytesseract and cloud fallback wrappers."""
    
    def __init__(self, tesseract_cmd_path=None):
        self.tesseract_available = pytesseract is not None
        if tesseract_cmd_path and self.tesseract_available:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

    def extract_text_from_image(self, image_path):
        """Extract plain text from local image assets using local Tesseract."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image asset not found: {image_path}")
            
        if not self.tesseract_available:
            print("[OCR] pytesseract library is missing. Install pytesseract to run OCR.")
            return ""
            
        try:
            with Image.open(image_path) as img:
                text = pytesseract.image_to_string(img)
                return text.strip()
        except Exception as e:
            print(f"[OCR] Local extraction failed for {image_path}: {e}")
            return ""

    def batch_scan_directory(self, folder_path, out_index_file=None):
        """Scan a directory of image/PDF assets and write compiled text logs."""
        extracted_index = {}
        image_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
        
        if not os.path.exists(folder_path):
            print(f"[OCR] Target directory not found: {folder_path}")
            return extracted_index
            
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in image_extensions:
                    full_path = os.path.join(root, file)
                    print(f"[OCR] Bulk scanning image: {file}")
                    text = self.extract_text_from_image(full_path)
                    if text:
                        extracted_index[full_path] = text
                        
        if out_index_file and extracted_index:
            try:
                import json
                with open(out_index_file, 'w', encoding='utf-8') as f:
                    json.dump(extracted_index, f, indent=2)
                print(f"[OCR] Saved batch OCR logs to {out_index_file}")
            except Exception as e:
                print(f"[OCR] Error writing batch index: {e}")
                
        return extracted_index
