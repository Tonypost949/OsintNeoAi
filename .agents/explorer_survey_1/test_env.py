import sys
import importlib

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

packages_to_test = [
    "pymupdf",
    "fitz",
    "pdfplumber",
    "pypdf",
    "PyPDF2",
    "pytesseract",
    "easyocr",
    "PIL",
    "bs4",
    "mailbox",
    "sqlite3",
    "pytest",
    "google.cloud.bigquery",
    "networkx",
    "pandas",
    "openpyxl",
    "tqdm",
    "fastapi",
    "uvicorn",
    "chardet",
    "dateutil",
    "pdfminer",
    "email",
    "hashlib",
    "magic",
    "tiktoken",
    "torch"
]

print("\n--- Package Statuses ---")
for pkg in packages_to_test:
    try:
        mod = importlib.import_module(pkg)
        ver = getattr(mod, "__version__", "installed")
        print(f"  [OK] {pkg}: {ver}")
    except ImportError as e:
        print(f"  [MISSING] {pkg}: {e}")
    except Exception as e:
        print(f"  [ERROR] {pkg}: {e}")
