import json
import re

content_path = r"C:\Users\HP\.gemini\antigravity\brain\2dfef4c3-8925-4be4-a79e-c8d4755f7c55\.system_generated\steps\675\content.md"

with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print("=== PARSING OPENCODE SHARE SESSION ===")

# Search for the session title, slug, and other basic details
title_m = re.search(r'"title"\s*:\s*"([^"]+)"', text)
dir_m = re.search(r'"directory"\s*:\s*"([^"]+)"', text)
slug_m = re.search(r'"slug"\s*:\s*"([^"]+)"', text)

print(f"Session Title: {title_m.group(1) if title_m else 'Unknown'}")
print(f"Working Dir  : {dir_m.group(1) if dir_m else 'Unknown'}")
print(f"Session Slug : {slug_m.group(1) if slug_m else 'Unknown'}")

# Let's extract any user prompts or assistant tool calls/responses
# We can scan the text for messages that have role: user or role: assistant
user_messages = re.findall(r'role\s*:\s*"user".*?content\s*:\s*"([^"]+)"', text)
for idx, um in enumerate(user_messages[:10]):
    print(f"User [{idx}]: {um}")
    
# Let's find any mention of files or scripts that were run/created
# We look for path strings, commands, or setup details
print("\n--- DETECTED FILES / COMMANDS IN SHARE DATA ---")
paths = set(re.findall(r'[a-zA-Z]:\\[\w\\\-\s\.]+\.\w+', text))
for p in sorted(paths)[:20]:
    print(f" - {p}")
