import pypdf

filepath = r"C:\Users\HP\Downloads\Adobe Downloads\dl\chen Combine February 28, 2026.pdf"

print(f"Reading {filepath}...")
try:
    reader = pypdf.PdfReader(filepath)
    print(f"Number of pages: {len(reader.pages)}")
    
    # Extract text from all pages and print non-empty ones
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            print(f"\n--- PAGE {i+1} ---")
            print(text[:1000]) # Print first 1000 chars of each page
            if len(text) > 1000:
                print("... [TRUNCATED] ...")
except Exception as e:
    print(f"Error: {e}")
