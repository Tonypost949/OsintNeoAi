import re

def clean_html(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    
    # Split by lines and only keep lines that don't look like raw CSS
    cleaned_lines = []
    for line in html.split('\n'):
        line = line.strip()
        if not line: continue
        # Skip lines that are obviously CSS rules
        if line.startswith('.') or line.startswith('@') or line.startswith('/*') or '{' in line or '}' in line:
            continue
        # Strip HTML tags
        line_no_tags = re.sub(r'<[^>]+>', ' ', line).strip()
        if line_no_tags:
            cleaned_lines.append(line_no_tags)
            
    text = " ".join(cleaned_lines)
    text = re.sub(r'\s+', ' ', text)
    
    if "Proper" in text or "Thomas" in text:
        print("Relevant text extracted:\n")
        idx = max(0, text.find("Proper") - 500)
        print(text[idx:idx+3000].encode('ascii', 'replace').decode('ascii'))
    else:
        print(text[:3000].encode('ascii', 'replace').decode('ascii'))

clean_html(r'C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7\.system_generated\steps\1495\content.md')
