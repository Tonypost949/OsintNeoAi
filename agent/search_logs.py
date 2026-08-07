with open("Makaveli_Conversation_Log.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if "gmail" in line.lower() or "email" in line.lower() or "photo" in line.lower():
            # Print a snippet of the line
            print(line[:120])
