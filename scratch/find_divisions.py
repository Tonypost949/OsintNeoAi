import re, json

html_file = r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e0259c57-0b03-45f8-956f-927ea22d1195\.system_generated\steps\5789\content.md'
with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Look for text structures, titles, department descriptions
paragraphs = re.findall(r'\"text\":\s*\"([^\"]+)\"', text)
print(f'JSON text fields: {len(paragraphs)}')
for p in paragraphs:
    if len(p) > 10:
        print('PARAGRAPH:', p)

words = ['Court Operations', 'Civil Process', 'Levying', 'Field Services', 'Custody Operations', 'Special Investigations', 'Barnes', 'Sheriff-Coroner', 'CFD', 'Contract Cities', 'Irvine']
for w in words:
    pos = text.find(w)
    if pos != -1:
        print(f'Found {w} at {pos}:', text[max(0, pos-100):min(len(text), pos+200)])
