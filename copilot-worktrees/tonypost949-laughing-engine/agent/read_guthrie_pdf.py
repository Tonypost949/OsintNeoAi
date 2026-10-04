import os
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

pdf_path = r"C:\Users\HP\Downloads\Adobe Downloads\dl\I have included the information regarding Ann Guthrie and the sp.pdf"

def read_pdf():
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print(f"Reading {pdf_path}...")
    
    if fitz:
        print("Using PyMuPDF (fitz)...")
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            print(f"--- Page {i} ---")
            print(page.get_text())
    elif PyPDF2:
        print("Using PyPDF2...")
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                print(f"--- Page {i} ---")
                print(page.extract_text())
    else:
        print("No PDF library installed. Please install PyMuPDF or PyPDF2.")

if __name__ == '__main__':
    read_pdf()
