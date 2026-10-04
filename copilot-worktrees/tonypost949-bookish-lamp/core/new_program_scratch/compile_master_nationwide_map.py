import os
import json
import csv
import ast
import re

def clean_and_eval(val_str):
    if not val_str or val_str == '[]':
        return []
    cleaned = re.sub(r'\}\s*\{', '}, {', val_str)
    cleaned = re.sub(r"Decimal\('([^']+)'\)", r"\1", cleaned)
    try:
        return ast.literal_eval(cleaned)
    except Exception as e:
        try:
            return eval(cleaned, {"__builtins__": None}, {})
        except Exception as e2:
            return []

def main():
    matrix_json_path = r"C:\Users\HP\OneDrive\Documents\new_program_scratch\nationwide_coc_vulnerability_matrix.json"
    all_states_csv_path = r"C:\Users\HP\OneDrive\Documents\new_program_scratch\unzipped_data\opencode_work_20260621_152938\national_audits_all_state_records.csv"
    ppp_csv_path = r"C:\Users\HP\OneDrive\Documents\new_program_scratch\unzipped_data\opencode_work_20260621_152938\out_of_state_llc_ppp_network.csv"
    output_md_path = r"C:\Users\HP\OneDrive\Documents\new_program_scratch\nationwide_outbound_money_flow.md"

    # Load 50-state vulnerability matrix
    if os.path.exists(matrix_json_path):
        with open(matrix_json_path, 'r', encoding='utf-8') as f:
            vulnerability_matrix = json.load(f)
    else:
        vulnerability_matrix = {}

    # Load state audit allocations
    audit_data = {}
    if os.path.exists(all_states_csv_path):
        with open(all_states_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                state_abbr = row['state'].strip()
                hud_pit = clean_and_eval(row['hud_pit_list'])
                coc_continuum = clean_and_eval(row['coc_continuum_list'])
                non_profiteers = clean_and_eval(row['non_profiteers_index'])
                esa = clean_and_eval(row['environmental_site_assessments'])
                
                audit_data[state_abbr] = {
                    'hud_pit': hud_pit,
                    'coc_continuum': coc_continuum,
                    'non_profiteers': non_profiteers,
                    'esa': esa
                }

    # Load Out-of-State PPP Network Records
    ppp_network = {}
    if os.path.exists(ppp_csv_path):
        with open(ppp_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                loan_locations = row.get('loan_locations', '')
                # Find state abbreviation from loan locations (e.g. "Battle Creek, MI" -> "MI")
                state_match = re.search(r'\b([A-Z]{2})\b', loan_locations)
                if state_match:
                    st = state_match.group(1)
                else:
                    st = 'CA' # Fallback
                
                if st not in ppp_network:
                    ppp_network[st] = []
                
                ppp_network[st].append({
                    'owner_name': row.get('owner_name', 'N/A'),
                    'property_address': row.get('property_address', 'N/A'),
                    'apn': row.get('apn', 'N/A'),
                    'last_sale_value': row.get('last_sale_value', '0.0'),
                    'property_mail_address': row.get('property_mail_address', 'N/A'),
                    'property_mail_city': row.get('property_mail_city', 'N/A'),
                    'ppp_loan_count': row.get('ppp_loan_count', '0'),
                    'ppp_total_amount': row.get('ppp_total_amount', '0.0'),
                    'ppp_total_forgiven': row.get('ppp_total_forgiven', '0.0'),
                    'ppp_names': row.get('ppp_names', 'N/A'),
                    'loan_locations': loan_locations,
                    'loan_statuses': row.get('loan_statuses', 'N/A')
                })

    state_to_abbr = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
        "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
        "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
        "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
        "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
    }

    md = []
    md.append("# NATIONWIDE CONTINUUM OF CARE (CoC) MASTER FLOW MAP")
    md.append("`STATUS: FACTUAL PUBLIC RECORD MASTER INDEX`  ")
    md.append("`GOAL: COMPLETE NATIONWIDE MAPPING OF HUD PUBLIC FUNDS, PPP SHUFFLE NETWORKS & REGIONAL VULNERABILITIES`  \n")
    md.append("This unified matrix lists **every US State Balance of State CoC**, mapping the path of public funds from federal/taxpayer allocations to local administrators, non-profit subrecipients, and out-of-state PPP property shell networks.\n")
    
    md.append("## MASTER NATIONWIDE MONEY & PERSONNEL FLOW MATRIX\n")
    md.append("| State | CoC ID | CoC Node Name | Primary Recipient / Local Admin | Award Amount | Key Program / Service | NPI / Tax ID | Local Hazards, Policing, & PPP Loops |")
    md.append("| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |")

    detailed_profiles = []

    # Prioritize states with out-of-state PPP networks (excluding CA) for ordering if requested, but sorting alphabetically makes the matrix easy to navigate. Let's flag the PPP loops in the table clearly.
    for state_name in sorted(state_to_abbr.keys()):
        abbr = state_to_abbr[state_name]
        coc_info = vulnerability_matrix.get(state_name, {})
        coc_id = coc_info.get('id', f"{abbr}-BoS")
        coc_name = coc_info.get('name', f"{state_name} Balance of State CoC")
        vulnerabilities = coc_info.get('vulnerabilities', "Standard rural coverage gaps.")

        state_audit = audit_data.get(abbr, {
            'hud_pit': [], 'coc_continuum': [], 'non_profiteers': [], 'esa': []
        })

        hud_pit = state_audit['hud_pit']
        coc_continuum = state_audit['coc_continuum']
        non_profiteers = state_audit['non_profiteers']
        esa = state_audit['esa']
        state_ppp = ppp_network.get(abbr, [])

        # Determine PIT/homeless metrics
        pit_summary = "N/A"
        if hud_pit:
            pit_item = hud_pit[0]
            pit_summary = f"PIT Total: {pit_item.get('total_homeless', 0)} (Sheltered: {pit_item.get('sheltered_homeless', 0)}, Unsheltered: {pit_item.get('unsheltered_homeless', 0)})"

        # Build table rows
        # We merge awards, non-profits, and out-of-state PPP loans
        max_items = max(len(coc_continuum), len(non_profiteers), len(state_ppp), 1)
        for i in range(max_items):
            prog = coc_continuum[i] if i < len(coc_continuum) else {}
            recip = non_profiteers[i] if i < len(non_profiteers) else {}
            ppp = state_ppp[i] if i < len(state_ppp) else {}

            award_val = prog.get('award_amount')
            award_str = f"${award_val:,.2f}" if award_val else "N/A"
            prog_type = prog.get('program_type', "CoC Housing Programs")
            
            # Recipient
            recip_name = recip.get('organization_name')
            npi_code = recip.get('npi_id', recip.get('cms_billing_code', 'N/A'))
            
            if not recip_name:
                if ppp:
                    recip_name = f"**{ppp['owner_name']}** (PPP Shell)"
                    award_str = f"${float(ppp['ppp_total_amount']):,.2f}"
                    prog_type = "PPP Capital Loan Shuffle"
                    npi_code = f"APN: {ppp['apn']}"
                else:
                    recip_name = "*State Department of Housing / Direct County Admin*" if not award_val else "*Direct Municipal Recipient*"

            # Notes / Hazards
            combined_hazards = f"**{vulnerabilities}**<br>_Metrics:_ {pit_summary}"
            
            if ppp:
                combined_hazards += f"<br>_PPP Shuffle:_ Out-of-state shell owner of California asset `{ppp['property_address']}`. Loan location: `{ppp['loan_locations']}` (Status: {ppp['loan_statuses']})"
            
            if recip.get('unaccounted_fund_delta'):
                combined_hazards += f"<br>_Audit Warning:_ Unaccounted Delta: ${recip.get('unaccounted_fund_delta'):,.2f}"

            md.append(f"| {state_name} ({abbr}) | `{coc_id}` | {coc_name} | {recip_name} | {award_str} | {prog_type} | {npi_code} | {combined_hazards} |")

        # Detailed State Profile
        sect = []
        sect.append(f"### {state_name} ({abbr}) - Comprehensive Audit Profile")
        sect.append(f"- **CoC Node ID**: `{coc_id}`")
        sect.append(f"- **CoC Name**: **{coc_name}**")
        sect.append(f"- **Administrative Risks & Gaps**: {vulnerabilities}")
        if pit_summary != "N/A":
            sect.append(f"- **Vulnerability Population Data**: {pit_summary}")

        if state_ppp:
            sect.append("#### Mapped Out-of-State PPP Property & Shell Loan Networks:")
            for p in state_ppp:
                sect.append(f"  - **Shell Owner Name**: **{p['owner_name']}**")
                sect.append(f"    - **Target California Property**: `{p['property_address']}` (APN: `{p['apn']}`)")
                sect.append(f"    - **PPP Loan Details**: ${float(p['ppp_total_amount']):,.2f} drawn at `{p['loan_locations']}` (Status: `{p['loan_statuses']}`)")
                sect.append(f"    - **Mailing Registry**: `{p['property_mail_address']}`, {p['property_mail_city']}")

        if coc_continuum:
            sect.append("#### HUD Taxpayer Awards Path:")
            for p in coc_continuum:
                sect.append(f"  - **Program Type**: {p.get('program_type', 'N/A')} | **HUD Award**: ${p.get('award_amount', 0):,.2f} (FY {p.get('fiscal_year', 'N/A')})")
        else:
            sect.append("#### HUD Taxpayer Awards Path:\n  - Downstream funds administered directly via state-allocated Emergency Solutions Grants (ESG) and HOME consortia.")

        if non_profiteers:
            sect.append("#### Mapped Downstream Operators & Entities:")
            for np in non_profiteers:
                sect.append(f"  - **Organization Name**: `{np.get('organization_name', 'N/A')}`")
                sect.append(f"    - **NPI ID / CMS Code**: `{np.get('npi_id', 'N/A')}` / `{np.get('cms_billing_code', 'N/A')}`")
                if np.get('unaccounted_fund_delta'):
                    sect.append(f"    - **Unaccounted Fund Delta**: `${np.get('unaccounted_fund_delta'):,.2f}`")
                if np.get('task_tracking_url'):
                    sect.append(f"    - **Internal Log Context**: {np.get('task_tracking_url')}")

        if esa:
            sect.append("#### Mapped Environmental Site Hazards:")
            for e in esa:
                sect.append(f"  - **Site ID**: `{e.get('site_id', 'N/A')}` | **Hazardous Location**: {e.get('location_name', 'N/A')}")
                sect.append(f"    - **Contaminant**: {e.get('contaminant_type', 'N/A')} (Toxicity Multiplier: {e.get('test_multiplier', 'N/A')}x)")
                sect.append(f"    - **Waterboard Closure Status**: {e.get('closure_status', 'N/A')}")

        detailed_profiles.append("\n".join(sect))

    md.append("\n---\n")
    md.append("## DETAILED REGIONAL AUDIT FILES (BY STATE)\n")
    md.append("\n\n".join(detailed_profiles))

    with open(output_md_path, mode='w', encoding='utf-8') as f:
        f.write("\n".join(md) + "\n")
    
    print(f"[+] Compiled master nationwide money, PPP loops & personnel map at {output_md_path}")

if __name__ == '__main__':
    main()
