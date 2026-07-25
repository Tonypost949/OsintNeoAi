# parse_mbox_to_bq.py - Parse the downloaded Gmail mbox and load to BigQuery
# Reads: C:/Users/HP/OneDrive/Apps/Google Download Your Data/All mail mbox
# Loads to: project-743aab84-f9a5-4ec7-954:national_audits.gmail_index

import mailbox, json, os, subprocess, re
from datetime import datetime
from email.header import decode_header
from email.utils import parsedate_to_datetime

MBOX_PATH = r"C:\Users\HP\OneDrive\Apps\Google? Download Your Data\All mail Including Spam and Trash-002.mbox"
OUT_NDJSON = r"C:\OsintNeoAi\takeout_raw\gmail_index.ndjson"
BQ_PROJECT = "project-743aab84-f9a5-4ec7-954"
BQ_TABLE   = "national_audits.gmail_index"

os.makedirs(r"C:\OsintNeoAi\takeout_raw", exist_ok=True)

def decode_str(s):
    if not s:
        return ""
    try:
        parts = decode_header(s)
        decoded = []
        for part, enc in parts:
            if isinstance(part, bytes):
                decoded.append(part.decode(enc or "utf-8", errors="replace"))
            else:
                decoded.append(str(part))
        return " ".join(decoded)
    except Exception:
        return str(s)

def extract_emails(s):
    if not s:
        return []
    return re.findall(r'[\w.+-]+@[\w.-]+\.\w+', s)

def parse_date(msg):
    try:
        return parsedate_to_datetime(msg.get("Date", "")).isoformat()
    except Exception:
        return None

print(f"[START] Opening mbox: {MBOX_PATH}")
mbox = mailbox.mbox(MBOX_PATH)

print(f"[PARSE] Writing NDJSON to {OUT_NDJSON}")
count = 0
with open(OUT_NDJSON, "w", encoding="utf-8") as fout:
    for msg in mbox:
        try:
            row = {
                "message_id":   msg.get("Message-ID", "").strip(),
                "date":         parse_date(msg),
                "subject":      decode_str(msg.get("Subject", "")),
                "from_addr":    decode_str(msg.get("From", "")),
                "to_addr":      decode_str(msg.get("To", "")),
                "cc_addr":      decode_str(msg.get("Cc", "")),
                "labels":       msg.get("X-Gmail-Labels", ""),
                "thread_id":    msg.get("X-GM-THRID", ""),
                "from_emails":  extract_emails(msg.get("From", "")),
                "to_emails":    extract_emails(msg.get("To", "")),
                "has_attach":   msg.is_multipart(),
            }
            fout.write(json.dumps(row) + "\n")
            count += 1
            if count % 10000 == 0:
                print(f"  ... {count:,} messages parsed")
        except Exception as e:
            pass

print(f"[DONE] {count:,} messages written to {OUT_NDJSON}")

# Load to BigQuery
print(f"[BQ] Loading to {BQ_PROJECT}:{BQ_TABLE}")
result = subprocess.run([
    "bq", "load",
    "--source_format=NEWLINE_DELIMITED_JSON",
    "--autodetect",
    "--replace",
    f"{BQ_PROJECT}:{BQ_TABLE}",
    OUT_NDJSON
], capture_output=True, text=True)

if result.returncode == 0:
    print(f"[BQ] ✅ Loaded {count:,} Gmail messages to {BQ_TABLE}")
else:
    print(f"[BQ] ❌ Error: {result.stderr}")
