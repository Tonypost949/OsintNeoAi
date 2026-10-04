import json
import re
import os

json_file = r"C:\Users\HP\Downloads\Orange-County-Structural-Failure-Investigation.json"
output_file = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\extracted_intelligence_summary.md"

def extract_intel():
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found.")
        return
        
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Extract user prompts and assistant responses
    dialogues = []
    entities = set()
    dates = set()
    case_numbers = set()
    
    # Simple regex to find case numbers and entities
    case_regex = re.compile(r'\b(?:[0-9]{2}[A-Z]{2}[0-9]{5}|HUD-[0-9\-]+|Case\s+#?[0-9a-zA-Z\-]+)\b', re.IGNORECASE)
    date_regex = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+[0-9]{1,2}(?:st|nd|rd|th)?,\s+[0-9]{4}\b|\b[0-9]{2}/[0-9]{2}/[0-9]{4}\b', re.IGNORECASE)
    
    entity_keywords = [
        "Viet America Society", "VAS", "360 Clinic", "2T Media", "Mercy House", "RPM Team", 
        "Shea Homes", "Shea Properties", "Shay Holmes", "Monex", "Minex", "Hoag Medical Group",
        "SPIN", "GAPP", "Yamada", "Andrew Do", "Dr. Ann Verma", "Ann Verma", "Sheriff Barnes", 
        "Don Barnes", "Paul Barnes", "Dr. Chau", "Dr. Clayton Chau", "Vince Tien", "Chris Wangsaporn"
    ]

    for message in data:
        role = message.get("role", "")
        contents = message.get("contents", [])
        text_content = ""
        for item in contents:
            if item.get("type") == "text":
                text_content += item.get("content", "")
                
        # Find entities
        for ent in entity_keywords:
            if ent.lower() in text_content.lower():
                entities.add(ent)
                
        # Find case numbers
        for match in case_regex.findall(text_content):
            case_numbers.add(match)
            
        # Find dates
        for match in date_regex.findall(text_content):
            dates.add(match)
            
        dialogues.append({
            "role": role,
            "text": text_content,
            "created_at": message.get("created_at", "")
        })
        
    # Compile markdown output
    md = []
    md.append("# Extracted Forensic Intelligence Summary")
    md.append("\n*This summary compiles all timelines, case identifiers, and entities extracted from the forensic chat logs.*")
    
    md.append("\n## 1. Key Entities Identified")
    for ent in sorted(entities):
        md.append(f"- **{ent}**")
        
    md.append("\n## 2. Case Identifiers & Docket Numbers")
    for case in sorted(case_numbers):
        md.append(f"- `{case}`")
        
    md.append("\n## 3. Timeline Markers")
    for date in sorted(dates):
        md.append(f"- {date}")
        
    md.append("\n## 4. Key Transcript Events & Assertions")
    for d in dialogues:
        if d["role"] == "user":
            # Highlight user's input/events
            if len(d["text"].strip()) > 30 and any(keyword in d["text"] for keyword in ["evict", "Verma", "Barnes", "Monex", "Minex", "Shea"]):
                md.append(f"\n### User Event Entry ({d['created_at']})")
                md.append(f"> {d['text'].strip()}")
                
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))
        
    print(f"Successfully compiled intelligence summary to {output_file}")

if __name__ == "__main__":
    extract_intel()
