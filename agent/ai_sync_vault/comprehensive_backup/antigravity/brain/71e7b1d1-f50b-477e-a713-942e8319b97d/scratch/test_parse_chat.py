import re
import os

fp = r"C:\Users\HP\Downloads\OSINTNeoAiXXL_chat.json"
if os.path.exists(fp):
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Let's split by "you asked"
    parts = content.split("you asked")
    print(f"Total 'you asked' parts: {len(parts)}")
    
    # Preview first 2 parsed entries
    for idx, part in enumerate(parts[1:3]):
        print(f"\n--- PART {idx+1} ---")
        # Extract timestamp
        time_match = re.search(r'message time:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', part)
        timestamp = time_match.group(1) if time_match else "Unknown"
        
        # Split by "gemini response"
        subparts = part.split("gemini response")
        user_msg = ""
        assistant_msg = ""
        if len(subparts) > 0:
            # User message is between timestamp and gemini response
            user_text = subparts[0]
            # remove message time line
            user_text = re.sub(r'message time:\s*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '', user_text)
            user_msg = user_text.strip()
        if len(subparts) > 1:
            assistant_msg = subparts[1].strip()
            
        print(f"Timestamp: {timestamp}")
        print(f"User message length: {len(user_msg)} chars (preview: {user_msg[:100]}...)")
        print(f"Assistant response length: {len(assistant_msg)} chars (preview: {assistant_msg[:100]}...)")
else:
    print("File not found")
