import os
import json
from datetime import datetime

transcript_path = r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e0259c57-0b03-45f8-956f-927ea22d1195\.system_generated\logs\transcript.jsonl'
output_dir = r'C:\Users\Amd949609\OsintNeoAi-1\docs\chat_logs'
output_dir2 = r'C:\Users\Amd949609\OsintNeoAi-1\legal_library'
os.makedirs(output_dir, exist_ok=True)

md_lines = [
    "# 💬 LIVE INVESTIGATION CHAT TRANSCRIPT & DIRECTIVE LOG",
    f"**Conversation ID:** `e0259c57-0b03-45f8-956f-927ea22d1195`  ",
    f"**Last Synchronized:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`  ",
    "**Scope:** Continuous real-time record of all user directives, legal strategy, forensic findings, and code executions.",
    "",
    "---",
    ""
]

if os.path.exists(transcript_path):
    turn_count = 0
    with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                step_type = entry.get('type')
                source = entry.get('source')
                content = entry.get('content', '')
                created_at = entry.get('created_at', '')

                if step_type == 'USER_INPUT' and content:
                    turn_count += 1
                    md_lines.append(f"### 👤 USER DIRECTIVE #{turn_count} ({created_at})")
                    md_lines.append("")
                    md_lines.append(f"> {content.strip()}")
                    md_lines.append("")
                    md_lines.append("---")
                    md_lines.append("")
                elif step_type == 'PLANNER_RESPONSE' and content:
                    # Filter out purely internal tool summaries if any
                    clean_content = content.strip()
                    if clean_content:
                        md_lines.append(f"### 🤖 INVESTIGATION AGENT RESPONSE ({created_at})")
                        md_lines.append("")
                        md_lines.append(clean_content)
                        md_lines.append("")
                        md_lines.append("---")
                        md_lines.append("")
            except Exception:
                pass

output_file1 = os.path.join(output_dir, 'LIVE_INVESTIGATION_CHAT_TRANSCRIPT.md')
output_file2 = os.path.join(output_dir2, 'LIVE_INVESTIGATION_CHAT_TRANSCRIPT.md')

with open(output_file1, 'w', encoding='utf-8') as f1:
    f1.write('\n'.join(md_lines))

with open(output_file2, 'w', encoding='utf-8') as f2:
    f2.write('\n'.join(md_lines))

# Sync to C:\OsintNeoAi
os.makedirs(r'C:\OsintNeoAi\docs\chat_logs', exist_ok=True)
with open(r'C:\OsintNeoAi\docs\chat_logs\LIVE_INVESTIGATION_CHAT_TRANSCRIPT.md', 'w', encoding='utf-8') as f3:
    f3.write('\n'.join(md_lines))

print(f"[+] Chat transcript synced successfully with {turn_count} user turns.")
