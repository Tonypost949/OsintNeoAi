import csv
import ast
import re
import os
import json

def clean_and_eval(val_str):
    if not val_str or val_str == '[]':
        return []
    # Replace adjacent dictionaries missing a comma (e.g. } { or }\n {) with }, {
    cleaned = re.sub(r'\}\s*\{', '}, {', val_str)
    # Replace Decimal('...') with float or just the number
    cleaned = re.sub(r"Decimal\('([^']+)'\)", r"\1", cleaned)
    # Replace None with None
    # ast.literal_eval handles None, True, False natively.
    try:
        return ast.literal_eval(cleaned)
    except Exception as e:
        # Fallback to eval with restricted globals if ast fails due to weird types
        try:
            return eval(cleaned, {"__builtins__": None}, {})
        except Exception as e2:
            print(f"Error parsing: {val_str} -> {e2}")
            return []

def main():
    csv_path = r"C:\Users\HP\OneDrive\Documents\new_program_scratch\unzipped_data\opencode_work_20260621_152938\national_audits_all_state_records.csv"
    output_md_path = r"C:\Users\HP\OneDrive\Documents\new_program_scratch\nationwide_outbound_money_flow.md"
    
    if not os.path.exists(csv_path):
        print(f"Error: Master CSV not found at {csv_path}")
        return

    records = []
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            state = row['state']
            hud_pit = clean_and_eval(row['hud_pit_list'])
            coc_continuum = clean_and_eval(row['coc_continuum_list'])
            non_profiteers = clean_and_eval(row['non_profiteers_index'])
            esa = clean_and_eval(row['environmental_site_assessments'])
            
            records.append({
                'state': state,
                'hud_pit': hud_pit,
                'coc_continuum': coc_continuum,
                'non_profiteers': non_profiteers,
                'esa': esa
            })

    # Let's generate a beautiful markdown file summarizing the flow of money
    md_content = []
    md_content.append("# NATIONWIDE OUTBOUND MONEY FLOW MAP")
    md_content.append("`STATUS: FACTUAL PUBLIC RECORD INDEX`  ")
    md_content.append("`GOAL: TRACE ALL TRANSFERS OF PUBLIC HOUSING & HOMELESSNESS ALLOCATIONS NATIONWIDE`  \n")
    md_content.append("This document traces the downstream recipients of HUD CoC awards, program funding, non-profit subrecipients, and documented personnel across all 50 states as recorded in national public administration audits.\n")
    
    md_content.append("## MASTER STATE-BY-STATE OUTBOUND TRANSFER MATRIX\n")
    md_content.append("| State | CoC ID | CoC Name | Primary Recipient/NGO | Award Amount | Key Program / Service | NPI / Tax ID | Key Personnel / Notes |")
    md_content.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    # Build the table and also collect detailed state sections
    detailed_sections = []
    
    for rec in sorted(records, key=lambda x: x['state']):
        state = rec['state']
        hud_pit = rec['hud_pit']
        coc_continuum = rec['coc_continuum']
        non_profiteers = rec['non_profiteers']
        esa = rec['esa']
        
        # We might have multiple CoCs or subrecipients. Let's align them.
        cocs = {}
        for pit in hud_pit:
            coc_id = pit.get('coc_number', 'N/A')
            cocs[coc_id] = {
                'name': pit.get('coc_name', 'N/A'),
                'total_homeless': pit.get('total_homeless', 0),
                'recipients': [],
                'programs': []
            }
            
        for prog in coc_continuum:
            coc_id = prog.get('coc_number', 'N/A')
            if coc_id not in cocs:
                cocs[coc_id] = {'name': 'N/A', 'total_homeless': 0, 'recipients': [], 'programs': []}
            cocs[coc_id]['programs'].append(prog)
            
        # Distribute non_profiteers
        # Since non_profiteers don't always have a strict coc_id in the row, we associate them with the state's main CoC
        state_cocs = list(cocs.keys())
        primary_coc = state_cocs[0] if state_cocs else 'N/A'
        
        # If there are no cocs mapped, add a default placeholder
        if not cocs:
            cocs['N/A'] = {'name': 'N/A', 'total_homeless': 0, 'recipients': [], 'programs': []}
            primary_coc = 'N/A'

        for np in non_profiteers:
            if primary_coc != 'N/A':
                cocs[primary_coc]['recipients'].append(np)
            else:
                cocs['N/A']['recipients'].append(np)

        # Generate table rows
        for coc_id, info in cocs.items():
            name = info['name']
            programs = info['programs']
            recipients = info['recipients']
            
            if not programs and not recipients:
                # Placeholders for states without documented outbound details
                md_content.append(f"| {state} | {coc_id} | {name} | *Direct County/State Admin* | $0.00 | CoC Administrative Oversight | N/A | Local public housing authority oversight. |")
            else:
                # We have some details. Let's merge them nicely.
                max_len = max(len(programs), len(recipients), 1)
                for i in range(max_len):
                    prog = programs[i] if i < len(programs) else {}
                    recip = recipients[i] if i < len(recipients) else {}
                    
                    recip_name = recip.get('organization_name', '*State/Local Lead Agency*')
                    award = f"${prog.get('award_amount', 0):,.2f}" if prog.get('award_amount') else "N/A"
                    prog_type = prog.get('program_type', 'CoC Supportive Services')
                    npi_id = recip.get('npi_id', recip.get('cms_billing_code', 'N/A'))
                    
                    notes_parts = []
                    if recip.get('unaccounted_fund_delta'):
                        notes_parts.append(f"Unaccounted Delta: ${recip.get('unaccounted_fund_delta'):,.2f}")
                    if recip.get('task_tracking_url') and len(recip.get('task_tracking_url')) > 50:
                        # Extract some description if it's text
                        notes_parts.append(recip.get('task_tracking_url')[:100] + "...")
                    
                    notes = " | ".join(notes_parts) if notes_parts else "Standard administrative allocation."
                    
                    md_content.append(f"| {state} | {coc_id} | {name} | **{recip_name}** | {award} | {prog_type} | {npi_id} | {notes} |")

        # Build detailed section for the state if they have detailed records
        if non_profiteers or esa or coc_continuum:
            sect = []
            sect.append(f"### {state} - Detailed Outbound Money Flow")
            if coc_continuum:
                sect.append("#### Documented CoC Award Allocations:")
                for p in coc_continuum:
                    sect.append(f"- **Program**: {p.get('program_type', 'N/A')} | **Award**: ${p.get('award_amount', 0):,.2f} (FY {p.get('fiscal_year', 'N/A')})")
            if non_profiteers:
                sect.append("#### Documented Downstream Recipients & Entities:")
                for np in non_profiteers:
                    sect.append(f"- **Entity Name**: `{np.get('organization_name', 'N/A')}`")
                    sect.append(f"  - **NPI ID / CMS Code**: `{np.get('npi_id', 'N/A')}` / `{np.get('cms_billing_code', 'N/A')}`")
                    if np.get('unaccounted_fund_delta'):
                        sect.append(f"  - **Unaccounted Fund Delta**: `${np.get('unaccounted_fund_delta'):,.2f}`")
                    if np.get('task_tracking_url'):
                        sect.append(f"  - **Audit Note / Log Summary**: {np.get('task_tracking_url')}")
            if esa:
                sect.append("#### Environmental Site Assessments & Constraints:")
                for e in esa:
                    sect.append(f"- **Site ID**: `{e.get('site_id', 'N/A')}` | **Location**: {e.get('location_name', 'N/A')}")
                    sect.append(f"  - **Contaminant**: {e.get('contaminant_type', 'N/A')} (Multiplier: {e.get('test_multiplier', 'N/A')}x)")
                    sect.append(f"  - **Status**: {e.get('closure_status', 'N/A')}")
            detailed_sections.append("\n".join(sect))

    if detailed_sections:
        md_content.append("\n---\n")
        md_content.append("## DETAILED STATE INVESTIGATIVE PROFILES\n")
        md_content.append("\n\n".join(detailed_sections))

    with open(output_md_path, mode='w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    print(f"[+] Successfully generated master outbound money flow map at {output_md_path}")

if __name__ == '__main__':
    main()
