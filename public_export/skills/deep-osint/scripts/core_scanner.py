#!/usr/bin/env python3
# core_scanner.py
# Minimal read-only full-device scanner (OCR optional)
# Usage: python core_scanner.py --root "<path>" --outdir "<path>" [--ocr]
import argparse, hashlib, re, subprocess
from pathlib import Path
from datetime import datetime
import pandas as pd
from docx import Document
try:
    import magic
except Exception:
    magic = None
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.I)
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b")
LONGNUM_RE = re.compile(r"\b[0-9]{9,18}\b")
def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
def extract_docx(path):
    try:
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return f"[ERROR DOCX: {e}]"
def extract_xlsx(path):
    try:
        x = pd.read_excel(path, sheet_name=None, dtype=str)
        parts = []
        for sname, df in x.items():
            parts.append(f"--- SHEET: {sname} ---")
            for row in df.fillna("").astype(str).values:
                parts.append(" | ".join(row))
        return "\n".join(parts)
    except Exception as e:
        return f"[ERROR XLSX: {e}]"
def extract_pdf(path):
    try:
        p = subprocess.run(["pdftotext","-layout","-nopgbrk",str(path),"-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        if p.returncode == 0:
            return p.stdout.decode("utf8", errors="ignore")
        else:
            return f"[pdftotext error: {p.stderr.decode('utf8', errors='ignore')}]"
    except Exception as e:
        return f"[ERROR PDF: {e}]"
def extract_image(path, use_ocr=False):
    if not use_ocr:
        return ""
    try:
        p = subprocess.run(["tesseract", str(path), "stdout", "-l", "eng"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        if p.returncode == 0:
            return p.stdout.decode("utf8", errors="ignore")
        else:
            return f"[tesseract error: {p.stderr.decode('utf8', errors='ignore')}]"
    except Exception as e:
        return f"[ERROR OCR: {e}]"
def read_text_file(path):
    try:
        return Path(path).read_text(encoding="utf8", errors="ignore")
    except Exception as e:
        return f"[ERROR READ: {e}]"
def detect_mime(path):
    if magic:
        try:
            return magic.from_file(str(path), mime=True)
        except Exception:
            return None
    return None
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--ocr", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    excel_path = outdir / f"osint_{timestamp}.xlsx"
    inventory = []
    extracted = []
    emails = set()
    phones = set()
    longnums = set()
    for p in root.rglob("*"):
        try:
            if not p.is_file():
                continue
            try:
                if outdir in p.resolve().parents or p.resolve() == outdir:
                    continue
            except Exception:
                pass
            sha = sha256_of_file(p)
            mtime = datetime.utcfromtimestamp(p.stat().st_mtime).isoformat() + "Z"
            size = p.stat().st_size
            inventory.append({"Path": str(p), "Size": size, "ModifiedUTC": mtime, "SHA256": sha})
            suffix = p.suffix.lower()
            text = ""
            if suffix == ".pdf":
                text = extract_pdf(p)
            elif suffix == ".docx":
                text = extract_docx(p)
            elif suffix in (".xlsx", ".xls"):
                text = extract_xlsx(p)
            elif suffix in (".txt", ".csv", ".log", ".json", ".xml", ".md"):
                text = read_text_file(p)
            elif suffix in (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"):
                text = extract_image(p, use_ocr=args.ocr)
            else:
                mime = detect_mime(p)
                if mime == "application/pdf":
                    text = extract_pdf(p)
                elif mime and mime.startswith("text"):
                    text = read_text_file(p)
                else:
                    text = ""
            if text:
                cap = 200000
                extracted.append({"Path": str(p), "ExtractedText": text[:cap]})
                for e in EMAIL_RE.findall(text):
                    emails.add(e.strip())
                for ph in PHONE_RE.findall(text):
                    phones.add(ph.strip())
                for ln in LONGNUM_RE.findall(text):
                    longnums.add(ln.strip())
            else:
                extracted.append({"Path": str(p), "ExtractedText": "[ORPHAN: no parsable text or unsupported binary]"})
        except Exception as ex:
            inventory.append({"Path": str(p), "Size": None, "ModifiedUTC": None, "SHA256": f"[ERROR HASH: {ex}]"})
            extracted.append({"Path": str(p), "ExtractedText": f"[ERROR PROCESSING: {ex}]"})
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        pd.DataFrame(inventory).to_excel(writer, sheet_name="FileInventory", index=False)
        pd.DataFrame(extracted).to_excel(writer, sheet_name="ExtractedTextIndex", index=False)
        pd.DataFrame(sorted(list(emails)), columns=["Email"]).to_excel(writer, sheet_name="Emails", index=False)
        pd.DataFrame(sorted(list(phones)), columns=["Phone"]).to_excel(writer, sheet_name="Phones", index=False)
        pd.DataFrame(sorted(list(longnums)), columns=["Number"]).to_excel(writer, sheet_name="Numbers", index=False)
        pd.DataFrame([], columns=["Type","Value","Sheet","Column","RowIndex","MatchedValueOrScore"]).to_excel(writer, sheet_name="Matches", index=False)
    inv_csv = outdir / f"dl_file_index_{timestamp}.csv"
    pd.DataFrame(inventory).to_csv(inv_csv, index=False)
    print("Wrote Excel:", excel_path)
    print("Wrote inventory CSV:", inv_csv)
if __name__ == "__main__":
    main()
