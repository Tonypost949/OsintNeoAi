import json

with open("Makaveli_Conversation_Log.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        content = data.get("content", "")
        if "email" in content.lower() or "gmail" in content.lower():
            # Look for numbers in the line
            for word in content.split():
                clean_word = "".join(c for c in word if c.isdigit() or c in [',', '.'])
                if clean_word and len(clean_word) >= 3:
                    print(f"Step {data.get('step_index')}: {word} | context: {content[:160]}...")
