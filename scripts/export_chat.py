#!/usr/bin/env python3
"""
OSINTNeoAi Chat Export Utility
Exports the full session chat transcript into Markdown, HTML, Plain Text, and JSON formats.
"""

import os
import json
import datetime

APP_DATA_DIR = r"C:\Users\Amd949609\.gemini\antigravity-cli"
CONV_ID = "e0259c57-0b03-45f8-956f-927ea22d1195"
TRANSCRIPT_PATH = os.path.join(APP_DATA_DIR, "brain", CONV_ID, ".system_generated", "logs", "transcript.jsonl")

EXPORT_DIR = r"C:\Users\Amd949609\OsintNeoAi-1\exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

def parse_transcript():
    if not os.path.exists(TRANSCRIPT_PATH):
        print(f"[-] Transcript file not found at: {TRANSCRIPT_PATH}")
        return []

    turns = []
    current_turn = {"user": None, "agent": None, "timestamp": None}

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                step_type = data.get("type", "")
                created_at = data.get("created_at", "")
                content = data.get("content", "")

                if step_type == "USER_INPUT":
                    if current_turn["user"] is not None:
                        turns.append(current_turn)
                        current_turn = {"user": None, "agent": None, "timestamp": None}
                    current_turn["user"] = content.strip()
                    current_turn["timestamp"] = created_at
                elif step_type == "PLANNER_RESPONSE":
                    if content and content.strip():
                        if current_turn["agent"]:
                            current_turn["agent"] += "\n\n" + content.strip()
                        else:
                            current_turn["agent"] = content.strip()
            except Exception:
                continue

    if current_turn["user"] is not None:
        turns.append(current_turn)

    return turns

def export_all():
    turns = parse_transcript()
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Export Markdown (.md)
    md_path = os.path.join(EXPORT_DIR, f"chat_export_{now_str}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 📜 OSINTNeoAi Session Chat Export\n")
        f.write(f"**Session ID:** `{CONV_ID}`  \n")
        f.write(f"**Export Timestamp:** `{datetime.datetime.now().isoformat()}`  \n")
        f.write(f"**Total Conversation Turns:** `{len(turns)}`\n\n---\n\n")
        
        for i, t in enumerate(turns, 1):
            f.write(f"### Turn {i}\n")
            if t['timestamp']:
                f.write(f"*Time:* `{t['timestamp']}`\n\n")
            f.write(f"**User:**\n```\n{t['user']}\n```\n\n")
            if t['agent']:
                f.write(f"**Antigravity Assistant:**\n\n{t['agent']}\n\n")
            f.write("---\n\n")
    print(f"[+] Exported Markdown: {md_path}")

    # 2. Export HTML (.html)
    html_path = os.path.join(EXPORT_DIR, f"chat_export_{now_str}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OSINTNeoAi Chat Export - {now_str}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ border-bottom: 2px solid #334155; padding-bottom: 15px; margin-bottom: 30px; }}
        .turn {{ background: #1e293b; border-radius: 10px; padding: 20px; margin-bottom: 20px; border-left: 4px solid #38bdf8; }}
        .user {{ color: #38bdf8; font-weight: bold; margin-bottom: 10px; }}
        .user-box {{ background: #0f172a; padding: 12px; border-radius: 6px; font-family: monospace; white-space: pre-wrap; }}
        .agent {{ color: #4ade80; font-weight: bold; margin-top: 15px; margin-bottom: 10px; }}
        .agent-box {{ background: #1e293b; line-height: 1.6; white-space: pre-wrap; }}
        .time {{ font-size: 0.8em; color: #94a3b8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📜 OSINTNeoAi Session Chat Export</h2>
            <p><strong>Session ID:</strong> {CONV_ID}</p>
            <p><strong>Export Date:</strong> {datetime.datetime.now().strftime('%B %d, %Y %I:%M %p')}</p>
            <p><strong>Total Turns:</strong> {len(turns)}</p>
        </div>
""")
        for i, t in enumerate(turns, 1):
            f.write(f"""
        <div class="turn">
            <div class="time">Turn {i} &bull; {t['timestamp']}</div>
            <div class="user">👤 User:</div>
            <div class="user-box">{t['user']}</div>
            <div class="agent">🤖 Assistant:</div>
            <div class="agent-box">{t['agent'] if t['agent'] else '<em>[Tool Call Step]</em>'}</div>
        </div>
""")
        f.write("    </div>\n</body>\n</html>")
    print(f"[+] Exported HTML: {html_path}")

    # 3. Export JSON (.json)
    json_path = os.path.join(EXPORT_DIR, f"chat_export_{now_str}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "session_id": CONV_ID,
            "export_timestamp": datetime.datetime.now().isoformat(),
            "total_turns": len(turns),
            "turns": turns
        }, f, indent=2)
    print(f"[+] Exported JSON: {json_path}")

    # Also keep a permanent 'latest' copy
    shutil_copy(md_path, os.path.join(EXPORT_DIR, "chat_export_latest.md"))
    shutil_copy(html_path, os.path.join(EXPORT_DIR, "chat_export_latest.html"))
    shutil_copy(json_path, os.path.join(EXPORT_DIR, "chat_export_latest.json"))

def shutil_copy(src, dst):
    import shutil
    shutil.copy2(src, dst)

if __name__ == "__main__":
    export_all()
