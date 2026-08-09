import os
import json
import re

downloads_path = r"C:\Users\HP\Downloads"

def find_names_in_file(file_path):
    print(f"\n=== Searching in {os.path.basename(file_path)} ===")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Search for names of residents or lists of individuals.
    # We can look for sections starting with "Resident", "Name", "Occupant", "Homeless", "List of", "Truthfinder"
    # Or look for common patterns of lists of names (2-3 words starting with capitals, maybe comma separated or on newlines)
    # Let's search for some patterns:
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # If the line contains "resident" or "names" or "homeless" or "truthfinder", print the context (lines before and after)
        if any(keyword in line.lower() for keyword in ["resident", "occupant", "homeless", "victim", "staying", "shelter"]):
            # Print 5 lines before and after
            start = max(0, i - 2)
            end = min(len(lines), i + 6)
            print(f"--- Context around line {i+1} ---")
            for j in range(start, end):
                print(f"{j+1}: {lines[j]}")
            print("-" * 30)

if __name__ == "__main__":
    find_names_in_file(os.path.join(downloads_path, "Huntington-Beach-Site-Investigation.txt"))
    find_names_in_file(os.path.join(downloads_path, "Orange-County-Structural-Failure-Investigation.json"))
