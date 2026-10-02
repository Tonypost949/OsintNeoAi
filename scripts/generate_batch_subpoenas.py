import json
import os

def generate_subpoenas():
    index_path = 'evidence/stormtech_legal_permit_index.json'
    out_dir = 'evidence/generated_subpoenas'
    os.makedirs(out_dir, exist_ok=True)
    
    if not os.path.exists(index_path):
        print(f"Error: {index_path} not found.")
        return
        
    with open(index_path, 'r', encoding='utf-8') as f:
        permits = json.load(f)
        
    template = """# OFFICIAL SUBPOENA DUCES TECUM & LEGAL NOTICE

**TARGET AGENCY / HOLDER:** {agency}
**PERMIT NUMBER:** {permit_no}
**PROJECT TITLE:** {title}
**START DATE:** {start_date}
**STATUS:** {status}

---

## MANDATORY DEMAND FOR PRODUCTION OF DOCUMENTS & ESI PRESESRVATION

YOU ARE HEREBY COMMANDED to produce and preserve all records, engineering schematics, cathodic protection tests, and inspection logs relating to underground pipe wrapping and storm drain installation for Permit No. **{permit_no}** ({agency}).

### CORRELATED ENVIRONMENTAL INVESTIGATION
This legal notice is served in conjunction with **OCHCA Case No. 20IC002** regarding Hexavalent Chromium (Cr-VI) contamination measured at 49x legal MCL limits near Monitoring Well **W-4150**.

### DESCRIPTION OF WORK UNDER PERMIT:
{desc}

---
*Notice issued under Master OSINT & Legal Preservation Protocol.*
"""

    count = 0
    for idx, p in enumerate(permits):
        agency = p.get('agency') or 'UNKNOWN_AGENCY'
        permit_no = p.get('permit_no') or f'PERMIT_{idx+1}'
        title = p.get('title') or 'N/A'
        start_date = p.get('start_date') or 'N/A'
        status = p.get('status') or 'N/A'
        desc = p.get('desc') or 'N/A'
        
        content = template.format(
            agency=agency,
            permit_no=permit_no,
            title=title,
            start_date=start_date,
            status=status,
            desc=desc
        )
        
        filename = f"subpoena_{idx+1:03d}_{permit_no.replace('/', '_')}.md"
        filepath = os.path.join(out_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as out_f:
            out_f.write(content)
        count += 1

    print(f"Successfully generated {count} subpoena documents in {out_dir}.")

if __name__ == '__main__':
    generate_subpoenas()
