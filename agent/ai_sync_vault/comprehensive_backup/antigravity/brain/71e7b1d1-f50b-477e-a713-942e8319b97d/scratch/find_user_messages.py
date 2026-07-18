import json

log_file = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\logs\transcript.jsonl"
with open(log_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
user_msgs = []
for line in lines:
    try:
        data = json.loads(line)
        if data.get('source') == 'USER_EXPLICIT':
            user_msgs.append((data.get('step_index'), data.get('content')))
    except Exception as e:
        pass

print("\n--- Recent User Messages ---")
for idx, msg in user_msgs[-30:]:
    print(f"Step {idx}: {msg}")
