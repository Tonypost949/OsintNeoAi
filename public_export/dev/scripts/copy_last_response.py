import os
import json
import pyperclip
from pathlib import Path

# Permanent AGY transcript path for this conversation session
TRANSCRIPT_PATH = Path(r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e616d655-4be6-4f57-bfad-24249ce3f54e\.system_generated\logs\transcript.jsonl')

def copy_last_agent_response():
    if not TRANSCRIPT_PATH.exists():
        print(f"❌ Transcript file not found: {TRANSCRIPT_PATH}")
        return None

    last_response = None
    with open(TRANSCRIPT_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                data = json.loads(line)
                # Look for PLANNER_RESPONSE or MODEL source steps
                if data.get('type') == 'PLANNER_RESPONSE' or data.get('source') == 'MODEL':
                    content = data.get('content')
                    if content and isinstance(content, str) and content.strip():
                        last_response = content.strip()
            except Exception:
                continue

    if last_response:
        pyperclip.copy(last_response)
        print("=========================================================")
        print("  📋 COPIED LAST AGENT RESPONSE DIRECTLY TO CLIPBOARD!   ")
        print("=========================================================")
        print(f"Preview (First 150 chars):\n{last_response[:150]}...")
        print("=========================================================")
        print("👉 Press [Ctrl + V] anywhere to paste!")
        return last_response
    else:
        print("❌ Could not find a valid model response in transcript.")
        return None

if __name__ == '__main__':
    copy_last_agent_response()
