import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def scan_file(fpath):
    print(f"\n========================================")
    print(f"Scanning: {fpath}")
    print(f"========================================")
    
    if not os.path.exists(fpath):
        print("File not found.")
        return
        
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            
        # DeepSeek exported JSON format is usually a list of conversation dicts
        # Let's inspect the structure
        if isinstance(data, dict):
            # If it's wrapped in a key
            conversations = data.get("conversations", [])
        elif isinstance(data, list):
            conversations = data
        else:
            print("Unknown JSON format structure.")
            return
            
        print(f"Found {len(conversations)} conversations.")
        
        terms = ["holes", "disgrace", "tamper", "suppress", "city sites", "other states"]
        
        for convo_idx, convo in enumerate(conversations):
            title = convo.get("title", f"Convo {convo_idx}")
            messages = convo.get("messages", [])
            
            # Check if any message contains our search terms
            convo_match = False
            matched_lines = []
            
            for msg_idx, msg in enumerate(messages):
                content = msg.get("content", "")
                role = msg.get("role", "unknown")
                
                # Check lines of the message
                lines = content.split('\n')
                for line_idx, line in enumerate(lines):
                    for term in terms:
                        if term in line.lower():
                            convo_match = True
                            matched_lines.append((msg_idx, role, line_idx+1, line.strip()))
                            break
                            
            if convo_match:
                print(f"\n--- MATCHED CONVERSATION: '{title}' ---")
                for msg_idx, role, line_num, text in matched_lines:
                    print(f"  Message #{msg_idx} [{role}] | Line {line_num}: {text[:200]}")
                    
    except Exception as e:
        print(f"Error scanning JSON: {e}")

def main():
    paths = [
        r"C:\Users\HP\Downloads\deepseek_data-2026-07-02\conversations.json",
        r"C:\Users\HP\Downloads\deepseek_data-2026-07-02 (1)\conversations.json"
    ]
    for p in paths:
        scan_file(p)

if __name__ == "__main__":
    main()
