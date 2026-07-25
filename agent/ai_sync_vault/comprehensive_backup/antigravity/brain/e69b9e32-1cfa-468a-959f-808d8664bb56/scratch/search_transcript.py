import json

transcript_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\logs\transcript.jsonl"

print("Searching transcript for USER_INPUT...")
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("type") == "USER_INPUT":
                print(f"User Input (Step {data.get('step_index')}): {data.get('content')}")
        except Exception as e:
            pass
