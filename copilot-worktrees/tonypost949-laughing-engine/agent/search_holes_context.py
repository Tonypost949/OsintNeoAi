"""
Searches the raw text files for the word "holes" to identify the city site vulnerabilities.
"""
import os

def main():
    chat_file = r"C:\Users\HP\Downloads\OSINTNeoAiXXL-Terminal-Assistance.txt"
    if not os.path.exists(chat_file):
        print(f"File not found: {chat_file}")
        return
        
    with open(chat_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    lines = content.split('\n')
    for line_no, l in enumerate(lines):
        if "holes" in l.lower():
            print(f"\n========================================")
            print(f"Match in OSINTNeoAiXXL-Terminal-Assistance.txt at Line {line_no + 1}")
            print(f"========================================")
            start = max(0, line_no - 4)
            end = min(len(lines), line_no + 5)
            for j in range(start, end):
                prefix = ">>> " if j == line_no else "    "
                print(f"{prefix}{lines[j]}")

if __name__ == "__main__":
    main()
