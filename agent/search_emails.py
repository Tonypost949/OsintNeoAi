import json

with open("Makaveli_Conversation_Log.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        content = data.get("content", "")
        # Search for mentions of emails, gmail, or BQ load counts
        if "emails" in content or "gmail" in content or "ingest" in content:
            print(f"Step {data.get('step_index')}: {content[:150]}...")
