import os
import json
import re

downloads_path = r"C:\Users\HP\Downloads"

def find_names_in_text(text):
    # Search for lists of names. A name is usually Capitalized First and Capitalized Last.
    # Let's search for lists of names that might represent residents.
    # Let's find lines with typical name patterns, e.g., "John Doe", "Doe, John"
    # Also look for tables or list formats (e.g. Bullet points followed by capitalized names)
    lines = text.split('\n')
    extracted_lines = []
    
    # Common name regex: Capitalized Word followed by optional Middle Initial and Capitalized Word
    # Or Lastname, Firstname
    name_pattern = re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b|\b[A-Z][a-z]+,\s+[A-Z][a-z]+\b')
    
    for i, line in enumerate(lines):
        # We want lines that have multiple names, or lines in a list format containing names
        # Let's see if the line matches a name, and does not contain generic code keywords
        if name_pattern.search(line):
            # Exclude lines with obvious code or system tags unless they represent actual data
            lower_line = line.lower()
            if not any(k in lower_line for k in ["import ", "def ", "class ", "return ", "http", "api", "json", "const ", "let ", "function", "var "]):
                # If the line contains typical words like "homeless", "resident", "victim", "occupant", or is part of a list
                extracted_lines.append((i+1, line.strip()))
                
    return extracted_lines

def run_extraction():
    files_to_check = [
        "Huntington-Beach-Site-Investigation.txt",
        "Orange-County-Structural-Failure-Investigation.json",
        "Technical-Data-Audit-Kickoff.txt",
        "OSINTNeoAiXXL-Terminal-Assistance.txt"
    ]
    
    output_data = []
    for fname in files_to_check:
        fpath = os.path.join(downloads_path, fname)
        if not os.path.exists(fpath):
            continue
        print(f"Reading {fname}...")
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines_with_names = find_names_in_text(content)
        output_data.append(f"\n=========================================\nFILE: {fname}\n=========================================\n")
        for line_num, line in lines_with_names:
            # Let's filter lines that contain at least one capitalized name
            # and seem like they might list people
            output_data.append(f"Line {line_num}: {line}")
            
    with open("extracted_names_check.txt", "w", encoding="utf-8") as out:
        out.write("\n".join(output_data))
    print("Done! Extracted content written to extracted_names_check.txt")

if __name__ == "__main__":
    run_extraction()
