import os
import json
import urllib.request

user_folder = r'C:\Amd949609_Antigravity_v1'
tabcopy_dir = os.path.join(user_folder, 'tools', 'tabcopy', 'html_dumps_session_2')
os.makedirs(tabcopy_dir, exist_ok=True)

tabs = [
    {
        'id': 1,
        'title': 'Tab Copy Options',
        'url': 'chrome-extension://micdllihgoppmejpecmkilggmaagfdmb/options.html',
        'host': 'micdllihgoppmejpecmkilggmaagfdmb',
        'type': 'extension'
    },
    {
        'id': 2,
        'title': 'Persistent AI Account Access Guide - Google Gemini',
        'url': 'https://gemini.google.com/app/e0c5f6761c99d4d7',
        'host': 'gemini.google.com',
        'type': 'gemini_session'
    },
    {
        'id': 3,
        'title': 'AI Cloud Auth Manager - Colab (Doc 1)',
        'url': 'https://colab.research.google.com/drive/167RtrxpfbTEmUpD4bTepZDOo8Xvju2Kn',
        'host': 'colab.research.google.com',
        'type': 'colab_notebook'
    },
    {
        'id': 4,
        'title': 'AI Cloud Auth Manager - Colab (Doc 2)',
        'url': 'https://colab.research.google.com/drive/1njH4qSqVqxOmLIO9ACSE5e7Q8xhry6gJ#scrollTo=a85l328ViSfS',
        'host': 'colab.research.google.com',
        'type': 'colab_notebook'
    }
]

print(f'Ingesting 4 tabs into {tabcopy_dir}...')

for t in tabs:
    host_clean = t['host'].replace('.', '_')
    filename = f"tab_{t['id']:02d}_{host_clean}.html"
    filepath = os.path.join(tabcopy_dir, filename)
    
    if t['url'].startswith('http'):
        try:
            req = urllib.request.Request(t['url'], headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode('utf-8', errors='ignore')
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Successfully fetched HTTP content for Tab {t['id']}: {filename}")
        except Exception as e:
            stub = f"<html><head><title>{t['title']}</title></head><body><h1>{t['title']}</h1><p>URL: {t['url']}</p><p>Status: Auth Protected Session / HTTP Fetch Fallback ({e})</p></body></html>"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(stub)
            print(f"Saved auth stub for Tab {t['id']}: {filename} ({e})")
    else:
        stub = f"<html><head><title>{t['title']}</title></head><body><h1>{t['title']}</h1><p>Protocol: chrome-extension://</p></body></html>"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(stub)
        print(f"Saved extension placeholder for Tab {t['id']}: {filename}")

digest_path = os.path.join(tabcopy_dir, 'BROWSER_TAB_COPY_SESSION_2_DIGEST.json')
with open(digest_path, 'w', encoding='utf-8') as f:
    json.dump({'timestamp': '2026-09-17 20:29:28', 'tabs': tabs}, f, indent=2)

print(f"Digest JSON saved at: {digest_path}")
