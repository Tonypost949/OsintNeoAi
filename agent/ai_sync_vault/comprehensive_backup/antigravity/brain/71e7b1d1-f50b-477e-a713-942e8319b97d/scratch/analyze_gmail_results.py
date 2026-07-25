import json
import os
import sys

# Force output to utf-8
sys.stdout.reconfigure(encoding='utf-8')

report_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\automated_gmail_report.json"

if not os.path.exists(report_path):
    print("Report file not found!")
    exit(1)

with open(report_path, "r", encoding="utf-8") as f:
    emails = json.load(f)

print(f"Total emails: {len(emails)}")

targets = ["gao", "fbi", "fincen", "hudoig", "odni", "sec", "bounce", "rejection", "undeliverable", "delivery status"]

matches = {t: [] for t in targets}

for email in emails:
    text = (email.get("subject", "") + " " + email.get("snippet", "") + " " + email.get("from", "")).lower()
    for t in targets:
        if t in text:
            matches[t].append(email)

for t, list_emails in matches.items():
    print(f"\nTarget: {t.upper()} - Count: {len(list_emails)}")
    # Print the matches
    for e in list_emails:
        print(f"  Date: {e.get('date')}")
        print(f"  From: {e.get('from')}")
        print(f"  Subj: {e.get('subject')}")
        print(f"  Snip: {e.get('snippet')[:300]}")
        print("-" * 50)
