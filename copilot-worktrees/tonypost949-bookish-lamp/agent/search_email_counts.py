import json

with open("Makaveli_Conversation_Log.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        content = data.get("content", "")
        if "processed" in content.lower() or "ingested" in content.lower() or "emails" in content.lower():
            if "gmail" in content.lower():
                print(f"Step {data.get('step_index')}: {content[:300]}")
