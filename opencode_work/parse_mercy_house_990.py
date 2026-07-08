import re
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

TEXT_PATH = r"C:\Users\HP\OneDrive\Documents\opencode_work\mercy_house_990_text.txt"
OUTPUT_PATH = r"C:\Users\HP\OneDrive\Documents\opencode_work\mercy_house_990_analysis.json"

with open(TEXT_PATH, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Join with line markers for context
text = ''.join(lines)

# Find key financial figures by searching backwards from keywords
def find_financial_value(text, keyword, max_lookback=500):
    idx = text.upper().find(keyword.upper())
    if idx == -1:
        return None, None
    snippet = text[max(0, idx-max_lookback):idx+200]
    # Find all dollar amounts in snippet (lines after keyword have the values)
    # Values are on lines immediately following the label
    after_keyword = text[idx:idx+1000]
    amounts = re.findall(r'^\s*([0-9,]+\.[0-9]{2})\s*$', after_keyword, re.MULTILINE)
    if amounts:
        return float(amounts[0].replace(',', '')), after_keyword[:300]
    return None, None

# Find all dollar amounts in a range
def find_amounts_in_range(text, start_kw, end_kws=None, max_chars=2000):
    start_idx = text.upper().find(start_kw.upper())
    if start_idx == -1:
        return []
    if end_kws:
        end_idx = min(len(text), start_idx + max_chars)
        for ekw in end_kws:
            ei = text.upper().find(ekw.upper(), start_idx)
            if ei != -1:
                end_idx = min(end_idx, ei)
    else:
        end_idx = min(len(text), start_idx + max_chars)

    section = text[start_idx:end_idx]
    amounts = re.findall(r'([0-9,]{1,3}(?:,[0-9]{3})*\.[0-9]{2})', section)
    return [float(a.replace(',', '')) for a in amounts]

print("=== KEY FIGURE SEARCH ===\n")

# Total assets
ta = find_amounts_in_range(text, "Total assets", ["Total liabilities", "Total net assets"], 1500)
print(f"Total assets values found: {ta[:5]}")
if ta:
    print(f"  Most likely: ${ta[0]:,.2f}" if ta else "")

# Total liabilities
tl = find_amounts_in_range(text, "Total liabilities", ["Net assets", "Total net assets"], 1000)
print(f"Total liabilities values found: {tl[:5]}")

# Total net assets
tna = find_amounts_in_range(text, "Total net assets", None, 800)
print(f"Total net assets values found: {tna[:5]}")
if tna:
    print(f"  Most likely: ${tna[0]:,.2f}" if tna else "")

# Total revenue (find revenue section first)
rev_section_end = text.upper().find("TOTAL EXPENSES")
rev_section_start = text.upper().find("REVENUE")
if rev_section_start != -1 and rev_section_end != -1 and rev_section_start < rev_section_end:
    rev_section = text[rev_section_start:rev_section_end]
    rev_amounts = re.findall(r'([0-9,]{1,3}(?:,[0-9]{3})*\.[0-9]{2})', rev_section)
    rev_nums = sorted([float(a.replace(',','')) for a in rev_amounts], reverse=True)
    print(f"\nRevenue section amounts (top 5): {rev_nums[:5]}")

# Total expenses
exp_section_start = text.upper().find("TOTAL EXPENSES")
exp_section_end = text.upper().find("STATEMENT OF CASH FLOWS")
if exp_section_start != -1:
    exp_section = text[exp_section_start:exp_section_start+2000] if exp_section_end == -1 else text[exp_section_start:exp_section_end]
    exp_amounts = re.findall(r'([0-9,]{1,3}(?:,[0-9]{3})*\.[0-9]{2})', exp_section)
    exp_nums = sorted([float(a.replace(',','')) for a in exp_amounts], reverse=True)
    print(f"\nExpense section amounts (top 5): {exp_nums[:5]}")

# Federal awards total
fed_start = text.upper().find("SCHEDULE OF EXPENDITURES OF FEDERAL AWARDS")
if fed_start != -1:
    fed_section = text[fed_start:fed_start+5000]
    fed_amounts = re.findall(r'([0-9,]{1,3}(?:,[0-9]{3})*\.[0-9]{2})', fed_section)
    fed_nums = sorted([float(a.replace(',','')) for a in fed_amounts], reverse=True)
    print(f"\nFederal awards amounts (top 10): {fed_nums[:10]}")

# Now look at the full activities section
print("\n\n=== DETAILED ACTIVITIES SECTION ===")
act_start = text.upper().find("COMBINED STATEMENTS OF ACTIVITIES")
if act_start != -1:
    act_end = text.upper().find("COMBINED STATEMENTS OF FUNCTIONAL EXPENSES")
    if act_end == -1:
        act_end = text.upper().find("STATEMENTS OF FUNCTIONAL EXPENSES")
    activities = text[act_start:act_end if act_end != -1 else act_start+8000]
    print(activities[:4000])
