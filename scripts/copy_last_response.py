import json
import os
import subprocess
import sys

def copy_last_message():
    app_data = os.path.expanduser(r"~\.gemini\antigravity-cli\brain")
    conv_id = "eecb0ad6-4ca2-42b9-8310-5d58aa9eb1db"
    log_file = os.path.join(app_data, conv_id, ".system_generated", "logs", "transcript.jsonl")
    
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return False
        
    last_response = None
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                # Look for PLANNER_RESPONSE or MODEL source with text content
                if data.get("type") == "PLANNER_RESPONSE" or data.get("source") == "MODEL":
                    content = data.get("content", "")
                    if content:
                        last_response = content
            except Exception:
                continue
                
    if not last_response:
        print("No response found to copy.")
        return False

    # Copy to Windows Clipboard via PowerShell Set-Clipboard
    process = subprocess.Popen(['powershell', '-Command', '$Input | Set-Clipboard'], stdin=subprocess.PIPE, text=True, encoding='utf-8')
    process.communicate(input=last_response)
    print("✓ Successfully copied the last assistant message to clipboard!")
    return True

if __name__ == "__main__":
    copy_last_message()
