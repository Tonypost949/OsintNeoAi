with open("OSINT Skill and Master Sheet Update.txt", "r", encoding="utf-8") as f:
    for line in f:
        line_lower = line.lower()
        if "email" in line_lower or "gmail" in line_lower or "100" in line_lower or "count" in line_lower:
            print(line.strip())
