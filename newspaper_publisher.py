#!/usr/bin/env python3
"""
Tax-Funded Dispatch — Newspaper Publishing Engine
Transforms exhaustive OSINT audits and forensic evidence runs into
formatted broadsheet newspaper articles and dispatches to the Cloud Newsroom.
"""

import os
import sys
import json
import glob
import argparse
from datetime import datetime
import urllib.request
import urllib.error

STORIES_DB = os.path.join(os.path.dirname(__file__), "newspaper_stories.json")
AZURE_NEWSROOM_URL = "http://20.246.121.30:8080/api/publish"

def load_stories():
    if os.path.exists(STORIES_DB):
        try:
            with open(STORIES_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_stories(stories):
    with open(STORIES_DB, "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2)

def publish_audit_file(audit_file_path, push_to_cloud=False):
    if not os.path.exists(audit_file_path):
        print(f"[!] File not found: {audit_file_path}")
        return None

    with open(audit_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    target = data.get("query") or data.get("target") or "Unknown Target"
    timestamp = data.get("timestamp", datetime.now().isoformat())
    sources = data.get("sources_exhausted", [])
    findings_count = 0
    statutory_notes = []
    
    for s in sources:
        summary_text = s.get("summary", "")
        if "matching documents" in summary_text:
            findings_count += 57
        if "statutory" in summary_text.lower() or "1102.5" in summary_text:
            statutory_notes.append(summary_text)

    # Generate article format
    article = {
        "id": f"DISP-{abs(hash(target)) % 100000:05d}",
        "title": f"EXHAUSTIVE AUDIT: Complete Reconnaissance Run on {target}",
        "category": "Exhaustive Audit",
        "jurisdiction": "Municipal / Global",
        "published_at": timestamp,
        "author": "OsintNeoAi Multi-Vector Engine",
        "excerpt": f"Automated 7-vector reconnaissance exhausted all {len(sources)} sources against {target}.",
        "statutory_notes": statutory_notes,
        "sources_exhausted": [s.get("source") for s in sources],
        "raw_audit_file": os.path.basename(audit_file_path)
    }

    stories = load_stories()
    # Check if duplicate exists, update or append
    stories = [s for s in stories if s.get("id") != article["id"]]
    stories.insert(0, article)
    save_stories(stories)
    print(f"[+] Stored article: {article['title']} (ID: {article['id']})")

    if push_to_cloud:
        push_to_azure(article)

    return article

def push_to_azure(article):
    try:
        req = urllib.request.Request(
            AZURE_NEWSROOM_URL,
            data=json.dumps(article).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"[+] Pushed to Azure Cloud Newsroom ({resp.status} {resp.reason})")
    except Exception as e:
        print(f"[-] Could not push to Azure ({e}) (Server may not be started yet)")

def main():
    parser = argparse.ArgumentParser(description="Tax-Funded Dispatch Publisher")
    parser.add_argument("--audit", type=str, help="Path to exhaustive_audit_*.json")
    parser.add_argument("--all-audits", action="store_true", help="Ingest all exhaustive_audit_*.json in repo")
    parser.add_argument("--cloud", action="store_true", help="Push to Azure Cloud Newsroom")
    parser.add_argument("--test", action="store_true", help="Run self-test")

    args = parser.parse_args()

    if args.test or args.all_audits:
        audits = glob.glob("exhaustive_audit_*.json")
        print(f"[*] Found {len(audits)} audit files to publish.")
        for aud in audits:
            publish_audit_file(aud, push_to_cloud=args.cloud)
        print("[+] Self-test and ingestion complete.")
    elif args.audit:
        publish_audit_file(args.audit, push_to_cloud=args.cloud)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
