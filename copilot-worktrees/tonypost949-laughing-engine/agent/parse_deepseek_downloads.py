"""
Parses both downloaded chat logs (JSON and TXT format) and formats them into clean, structured Markdown files.
"""
import os
import json

def parse_deepseek_json(src, dst):
    print(f"Parsing DeepSeek JSON: {src} -> {dst}")
    try:
        with open(src, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        out = []
        out.append("# DeepSeek Chat Archive: Dehashed HBPD Scan\n")
        out.append(f"*Source File: {os.path.basename(src)}*\n\n")
        
        messages = data if isinstance(data, list) else data.get("messages", [])
        
        for msg in messages:
            role = str(msg.get("role", "")).upper()
            created = msg.get("created_at", "N/A")
            
            contents = msg.get("contents", [])
            content_str = ""
            if isinstance(contents, list):
                content_str = "\n".join([str(c.get("content", "")) for c in contents if "content" in c])
            else:
                content_str = str(msg.get("content", ""))
                
            out.append(f"## {role} ({created})\n")
            out.append(f"{content_str}\n\n---\n\n")
            
        with open(dst, 'w', encoding='utf-8') as f:
            f.write("".join(out))
        print("Success.")
        return True
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return False

def parse_gemini_txt(src, dst):
    print(f"Parsing Gemini TXT: {src} -> {dst}")
    try:
        with open(src, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        out = []
        out.append("# Gemini Chat Archive: OSINTNeoAiXXL Terminal Assistance\n")
        out.append(f"*Source File: {os.path.basename(src)}*\n\n")
        
        current_block = []
        for line in lines:
            # Detect message headers
            if line.strip() == "you asked":
                if current_block:
                    out.append("".join(current_block))
                    current_block = []
                current_block.append("## USER\n\n")
            elif line.strip() in ["gemini response", "deepseek response"]:
                if current_block:
                    out.append("".join(current_block))
                    current_block = []
                current_block.append("## ASSISTANT\n\n")
            elif line.strip().startswith("message time:"):
                current_block.append(f"*{line.strip()}*\n\n")
            else:
                # Add line content
                current_block.append(line)
                
        if current_block:
            out.append("".join(current_block))
            
        # Write to output file
        with open(dst, 'w', encoding='utf-8') as f:
            f.write("".join(out))
        print("Success.")
        return True
    except Exception as e:
        print(f"Failed to parse TXT: {e}")
        return False

def main():
    dl_dir = r"C:\Users\HP\Downloads"
    
    chat1_src = os.path.join(dl_dir, "Dehashed-HBPD-scan.json")
    chat2_src = os.path.join(dl_dir, "OSINTNeoAiXXL-Terminal-Assistance.txt")
    
    parse_deepseek_json(chat1_src, "deepseek_session_dehashed_hbpd.md")
    parse_gemini_txt(chat2_src, "gemini_session_osint_neoai_xxl.md")

if __name__ == "__main__":
    main()
