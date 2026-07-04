import re
import sys

def clean_html(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    
    # Very simple HTML strip
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
    except ImportError:
        text = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.DOTALL)
        text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
    
    # Also grab specific keywords
    if "Thomas" in text or "Proper" in text:
        print("Relevant text extracted:\n")
        # Extract 2000 chars around the first mention
        idx = max(0, text.find("Proper") - 500)
        print(text[idx:idx+2500].encode('ascii', 'replace').decode('ascii'))
    else:
        print(text[:3000].encode('ascii', 'replace').decode('ascii'))

clean_html(r'C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7\.system_generated\steps\1495\content.md')
