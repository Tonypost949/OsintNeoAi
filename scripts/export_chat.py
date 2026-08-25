#!/usr/bin/env python3
"""
OSINTNeoAi Master Chat Export Utility
Exports the complete session chat transcript into Markdown, HTML, Plain Text, and JSON formats
across exports/, docs/chat_logs/, and C:/OsintNeoAi/exports/.
"""

import os
import json
import datetime
import shutil

APP_DATA_DIR = r"C:\Users\Amd949609\.gemini\antigravity-cli"
CONV_ID = "e0259c57-0b03-45f8-956f-927ea22d1195"
TRANSCRIPT_PATH = os.path.join(APP_DATA_DIR, "brain", CONV_ID, ".system_generated", "logs", "transcript.jsonl")

EXPORT_DIRS = [
    r"C:\Users\Amd949609\OsintNeoAi-1\exports",
    r"C:\Users\Amd949609\OsintNeoAi-1\docs\chat_logs",
    r"C:\OsintNeoAi\exports"
]

for d in EXPORT_DIRS:
    os.makedirs(d, exist_ok=True)

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
    formatted_date = datetime.datetime.now().strftime('%B %d, %Y %I:%M:%S %p')
    
    print(f"[+] Total Conversation Turns Loaded: {len(turns)}")

    # 1. Build Markdown (.md)
    md_content = f"# 📜 OSINTNeoAi Session Chat Export\n"
    md_content += f"**Session ID:** `{CONV_ID}`  \n"
    md_content += f"**Export Date:** {formatted_date}  \n"
    md_content += f"**Total Conversation Turns:** `{len(turns)}`\n\n---\n\n"
    
    for i, t in enumerate(turns, 1):
        md_content += f"### Turn {i}\n"
        if t['timestamp']:
            md_content += f"*Time:* `{t['timestamp']}`\n\n"
        md_content += f"**👤 User:**\n```\n{t['user']}\n```\n\n"
        if t['agent']:
            md_content += f"**🤖 Assistant:**\n\n{t['agent']}\n\n"
        else:
            md_content += f"**🤖 Assistant:** *(Tool Execution Step)*\n\n"
        md_content += "---\n\n"

    # 2. Build HTML (.html)
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OSINTNeoAi Complete Chat Export - {now_str}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 25px; line-height: 1.5; }}
        .container {{ max-width: 960px; margin: 0 auto; }}
        .header {{ background: #1e293b; border-radius: 12px; padding: 25px; margin-bottom: 30px; border: 1px solid #334155; }}
        .header h1 {{ margin: 0 0 10px 0; color: #38bdf8; font-size: 24px; }}
        .header p {{ margin: 5px 0; color: #94a3b8; font-size: 14px; }}
        .badge {{ display: inline-block; background: #0284c7; color: white; padding: 4px 10px; border-radius: 9999px; font-weight: bold; font-size: 12px; }}
        .turn {{ background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 25px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2); }}
        .turn-header {{ display: flex; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 15px; }}
        .turn-number {{ font-weight: bold; color: #38bdf8; font-size: 16px; }}
        .timestamp {{ font-size: 12px; color: #64748b; }}
        .user-block {{ background: #0f172a; border-left: 4px solid #38bdf8; padding: 14px; border-radius: 6px; margin-bottom: 15px; font-family: monospace; white-space: pre-wrap; color: #e2e8f0; font-size: 14px; }}
        .agent-block {{ background: #182234; border-left: 4px solid #4ade80; padding: 16px; border-radius: 6px; white-space: pre-wrap; font-size: 14px; color: #f1f5f9; }}
        .label {{ font-weight: bold; margin-bottom: 6px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .user-label {{ color: #38bdf8; }}
        .agent-label {{ color: #4ade80; }}
        pre {{ background: #0b1120; padding: 10px; border-radius: 4px; overflow-x: auto; }}
        code {{ font-family: monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📜 OSINTNeoAi Complete Master Chat Export</h1>
            <p><strong>Session ID:</strong> {CONV_ID}</p>
            <p><strong>Export Date:</strong> {formatted_date}</p>
            <p><strong>Total Turns:</strong> <span class="badge">{len(turns)} Turns</span></p>
        </div>
"""
    for i, t in enumerate(turns, 1):
        user_text = t['user'] if t['user'] else ""
        agent_text = t['agent'] if t['agent'] else "[Tool Call Execution Step]"
        html_content += f"""
        <div class="turn">
            <div class="turn-header">
                <span class="turn-number">Turn #{i}</span>
                <span class="timestamp">{t['timestamp']}</span>
            </div>
            <div class="label user-label">👤 User</div>
            <div class="user-block">{user_text}</div>
            <div class="label agent-label">🤖 Antigravity Assistant</div>
            <div class="agent-block">{agent_text}</div>
        </div>
"""
    html_content += "    </div>\n</body>\n</html>"

    # 3. Build JSON (.json)
    json_data = {
        "session_id": CONV_ID,
        "export_timestamp": datetime.datetime.now().isoformat(),
        "total_turns": len(turns),
        "turns": turns
    }

    # Save to all target directories
    for export_dir in EXPORT_DIRS:
        # Timestamped files
        with open(os.path.join(export_dir, f"chat_export_{now_str}.md"), "w", encoding="utf-8") as f:
            f.write(md_content)
        with open(os.path.join(export_dir, f"chat_export_{now_str}.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
        with open(os.path.join(export_dir, f"chat_export_{now_str}.json"), "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        # 'Latest' pointer files
        with open(os.path.join(export_dir, "chat_export_latest.md"), "w", encoding="utf-8") as f:
            f.write(md_content)
        with open(os.path.join(export_dir, "chat_export_latest.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
        with open(os.path.join(export_dir, "chat_export_latest.json"), "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
            
        print(f"[+] Successfully exported all formats to: {export_dir}")

if __name__ == "__main__":
    export_all()
