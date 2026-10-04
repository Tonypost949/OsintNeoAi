import os
import json
import re

directories = [
    r"C:\Users\HP\Downloads",
    r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent"
]

def scan_all():
    found_matches = []
    # We want to look for sequences of names. E.g. lists containing multiple lines of names,
    # or specific sections mentioning names of homeless or shelter residents.
    for directory in directories:
        if not os.path.exists(directory):
            continue
        print(f"Scanning directory: {directory}")
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.txt', '.json', '.md', '.csv', '.html')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Let's search for "homeless" or "resident" or "names" or specific name listings
                        # Let's count how many names (First Last) are in the file
                        name_pattern = re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b')
                        names = name_pattern.findall(content)
                        
                        # If there is a high concentration of names, or specific keywords
                        if "17642" in content or "17631" in content or "cameron" in content.lower():
                            # Let's search for names near these addresses
                            # or look for lines that contain names and some indicator of a shelter or resident list
                            lines = content.split('\n')
                            for idx, line in enumerate(lines):
                                if any(kw in line.lower() for kw in ["shelter", "homeless", "resident", "occupant", "victim", "staying", "truthfinder", "dob", "ssn", "age"]):
                                    # Print matching lines and check for names nearby
                                    context = lines[max(0, idx-5):min(len(lines), idx+15)]
                                    found_matches.append({
                                        "file": file,
                                        "line_num": idx + 1,
                                        "text": line.strip(),
                                        "context": "\n".join(context)
                                    })
                    except Exception as e:
                        print(f"Error scanning {file}: {e}")
                        
    # Save the output
    with open("detailed_residents_scan.json", "w", encoding="utf-8") as out_f:
        json.dump(found_matches, out_f, indent=2)
    print(f"Scan complete. Found {len(found_matches)} context matches. Saved to detailed_residents_scan.json")

if __name__ == "__main__":
    scan_all()
