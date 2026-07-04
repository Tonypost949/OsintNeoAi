import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    target_path = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_documents\bigscan.html"
    if not os.path.exists(target_path):
        print(f"File not found: {target_path}")
        return
        
    print("Searching bigscan.html...")
    try:
        with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Let's search for status results like "200", "403", "302" or log elements
        lines = content.split('\n')
        print(f"Total lines: {len(lines)}")
        
        # Check if there is a JSON string or log text at the end of the file
        matches = []
        for idx, line in enumerate(lines):
            clean = re.sub('<[^<]+?>', '', line).strip()
            if not clean:
                continue
            # Look for domain scan status results or comments about exposed paths
            if any(term in clean.lower() for term in ["exposed", "vulnerable", "status", "result", "open", "disgrace"]):
                matches.append((idx+1, clean))
                
        print(f"Found {len(matches)} matches:")
        for idx, m in matches[:100]:
            print(f"Line {idx}: {m[:150]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
