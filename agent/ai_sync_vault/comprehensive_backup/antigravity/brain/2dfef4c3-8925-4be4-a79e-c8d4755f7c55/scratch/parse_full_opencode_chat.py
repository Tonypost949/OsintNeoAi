import json
import re

content_path = r"C:\Users\HP\.gemini\antigravity\brain\2dfef4c3-8925-4be4-a79e-c8d4755f7c55\.system_generated\steps\675\content.md"

with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's find all occurrences of $R[...] structures or the message arrays
print("=== PARSING OPENCODE HYDRATION ARRAY ===")

# Hydrated arrays in SolidJS look like $R[22]={...} or similar
# Let's find all $R[<num>] = {...} assignments in the script
assignments = re.findall(r'\$R\[(\d+)\]=([^;]+)', text)
print(f"Found {len(assignments)} hydrated state assignments.")

chat_log = []
for idx, val in assignments:
    # Look for role and content in the value
    if 'role' in val:
        try:
            # clean up value to parse as JSON if possible, or extract fields via regex
            role_m = re.search(r'role\s*:\s*"([^"]+)"', val)
            text_m = re.search(r'content\s*:\s*"([^"]+)"', val)
            code_m = re.search(r'code\s*:\s*"([^"]+)"', val)
            
            role = role_m.group(1) if role_m else "unknown"
            content = text_m.group(1) if text_m else ""
            
            # Unescape newlines and slashes
            content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
            
            chat_log.append({
                "index": int(idx),
                "role": role,
                "content": content
            })
        except:
            pass

print(f"Extracted {len(chat_log)} chat elements.")
for msg in sorted(chat_log, key=lambda x: x["index"]):
    print(f"\n--- [{msg['role'].upper()}] (Hydration ID: {msg['index']}) ---")
    print(msg['content'][:1500]) # Print first 1500 chars of each message
