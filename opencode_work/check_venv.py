import subprocess, os, sys

venv_py = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\venv\Scripts\python.exe"
checks = [
    ("PyMuPDF", "import fitz; print('OK', fitz.version[0])"),
    ("google.genai", "import google.genai; print('OK')"),
    ("PIL", "from PIL import Image; print('OK')"),
]

for name, code in checks:
    try:
        result = subprocess.run([venv_py, "-c", code], capture_output=True, text=True, timeout=15)
        out = result.stdout.strip() or result.stderr.strip()
        print(f"{name}: {out}")
    except Exception as e:
        print(f"{name}: ERROR - {e}")
