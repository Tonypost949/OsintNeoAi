import json

# Load the file, assuming it might have some formatting issues, so let's just read it directly.
# The article content was stored in a javascript object `window.__PRELOADED_STATE__`.

def extract_article_text():
    with open(r'C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7\.system_generated\steps\1495\content.md', 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    # The actual text of the article is usually embedded inside JSON data block or deep in <p> tags
    import re
    # Find all paragraph tags
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE | re.DOTALL)
    
    # Clean the tags inside paragraphs
    cleaned_paragraphs = []
    for p in paragraphs:
        text = re.sub(r'<[^>]+>', '', p).strip()
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 20: # Filter out short junk
            cleaned_paragraphs.append(text)
            
    print("--- EXTRACTED PARAGRAPHS ---\n")
    for i, p in enumerate(cleaned_paragraphs):
        print(f"[{i+1}] {p}".encode('ascii', 'replace').decode('ascii'))

extract_article_text()
