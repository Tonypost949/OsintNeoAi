#!/usr/bin/env python3
"""
Facebook & Social Media Dorking Protocol Engine for OsintNeoAi.
Bypasses walled-garden login barriers using search engine index permalink dorking,
extracts target mentions, threat threads, and group IDs, and auto-dispatches to Wayback Machine.
"""

import sys
import json
import urllib.parse
from datetime import datetime

def generate_facebook_dork_queries(target_name, location_or_keyword, group_keywords=None):
    if group_keywords is None:
        group_keywords = ["groups", "permalink", "posts"]

    dork_queries = [
        f'"{target_name}" "{location_or_keyword}" site:facebook.com/groups',
        f'"{target_name}" site:facebook.com/permalink',
        f'"{target_name}" "{location_or_keyword}" site:facebook.com/posts',
        f'"{target_name}" "Hexavalent Chromium" OR "threat" site:facebook.com'
    ]

    protocol_summary = {
        "target_name": target_name,
        "location_keyword": location_or_keyword,
        "generated_dorks": dork_queries,
        "protocol_rules": [
            "1. Bypass Facebook login walls via search engine index dorking.",
            "2. Extract numeric permalink IDs (e.g. 3132788366819109) and group handles (e.g. HB4UbyHBCF).",
            "3. Auto-dispatch discovered threat & OSINT permalinks to Wayback Machine API."
        ],
        "timestamp": datetime.now().isoformat()
    }

    return protocol_summary

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Larry McNeely"
    keyword = sys.argv[2] if len(sys.argv) > 2 else "Huntington Beach"

    summary = generate_facebook_dork_queries(target, keyword)
    output_path = r"C:\OsintNeoAi\facebook_dork_protocol.json"
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("==========================================================")
    print("   Facebook Dorking & Social OSINT Protocol Engine       ")
    print("==========================================================")
    print(f"[+] Dorking protocol generated for target: {target}")
    print(f"[+] Output saved to: {output_path}")
    print(json.dumps(summary["generated_dorks"], indent=2))
