libs = ['pypdf', 'PyPDF2', 'fitz', 'pdfplumber', 'pdfminer']
for lib in libs:
    try:
        __import__(lib)
        print(f"Import {lib} succeeded!")
    except ImportError:
        print(f"Import {lib} failed.")
