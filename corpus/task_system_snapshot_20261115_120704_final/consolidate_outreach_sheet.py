import csv
import json
import re

# 1. Read existing rows from downloaded Google Sheet
existing_rows = []
try:
    with open("/mnt/c/Amd949609_Antigravity_v1/summaries/LIVE_GOOGLE_SHEET_EXPORT.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                existing_rows.append(row)
except Exception as e:
    print("Error reading existing sheet:", e)

headers = ["Date", "Sector", "Entity/Recipient", "Subject/Topic", "Summary/Notes"]

# Standardize existing rows into clean 5-column format
clean_records = []
for idx, r in enumerate(existing_rows):
    if idx == 0 and "Date" in r[0]:
        continue
    while len(r) < 5:
        r.append("")
    clean_records.append({
        "Date": r[0].strip(),
        "Sector": r[1].strip(),
        "Entity/Recipient": r[2].strip(),
        "Subject/Topic": r[3].strip(),
        "Summary/Notes": r[4].strip()
    })

print(f"Loaded {len(clean_records)} clean records from current Google Sheet.")

# 2. Parse GMAIL_OUTREACH_TIMELINE.md to extract all unrecorded outreach entries
with open("/mnt/c/OsintNeoAi/GMAIL_OUTREACH_TIMELINE.md", "r", encoding="utf-8") as f:
    timeline_text = f.read()

# Pattern for markdown tables: | Date | Target | Subject | Status |
table_pattern = re.findall(r"\|\s*([^|\n]+?)\s*\|\s*([^|\n]+?)\s*\|\s*([^|\n]+?)\s*\|\s*([^|\n]+?)\s*\|", timeline_text)

print(f"Extracted {len(table_pattern)} raw table rows from GMAIL_OUTREACH_TIMELINE.md.")

def determine_sector(target):
    t = target.lower()
    if any(k in t for k in ["senator", "rep.", "doj", "fbi", "epa", "hud", "sec", "cftc", "usao", "attorney", "court", "assembly", "aps", "hca", "cdph", "fema", "edd", "white house", "task force", "bureau"]):
        return "Public Sector"
    elif any(k in t for k in ["aclu", "amnesty", "earthjustice", "disability rights", "narf", "friendship shelter", "legal aid", "non-profit", "church", "ngo"]):
        return "NGO & Non-Profit"
    elif any(k in t for k in ["school", "college", "university", "chapman", "ucla", "usc", "berkeley", "stanford"]):
        return "Academic / Legal Clinics"
    else:
        return "Private Sector"

# Add newly extracted records if not already in clean_records
existing_signatures = set()
for rec in clean_records:
    sig = (rec["Date"].lower(), rec["Entity/Recipient"][:30].lower(), rec["Subject/Topic"][:30].lower())
    existing_signatures.add(sig)

new_count = 0
for date_str, target_str, subject_str, status_str in table_pattern:
    date_clean = date_str.replace("**", "").strip()
    target_clean = target_str.replace("**", "").strip()
    subject_clean = subject_str.replace("**", "").strip()
    status_clean = status_str.replace("**", "").strip()

    if date_clean.lower() in ["date", "---", ""]:
        continue

    sig = (date_clean.lower(), target_clean[:30].lower(), subject_clean[:30].lower())
    if sig not in existing_signatures:
        sector = determine_sector(target_clean)
        clean_records.append({
            "Date": date_clean,
            "Sector": sector,
            "Entity/Recipient": target_clean,
            "Subject/Topic": subject_clean,
            "Summary/Notes": f"Status: {status_clean}. Transmitted/recorded via Relator outreach."
        })
        existing_signatures.add(sig)
        new_count += 1

print(f"Integrated {new_count} new entries from GMAIL_OUTREACH_TIMELINE.md. Total records: {len(clean_records)}")

# 3. Add latest 2026-10-18 staged FCA/RICO transmittals from 08_EMAIL_DRAFTS_UNSENT.md
staged_entries = [
    {
        "Date": "Oct 18, 2026",
        "Sector": "Public Sector",
        "Entity/Recipient": "U.S. Attorney's Office (C.D. Cal.)",
        "Subject/Topic": "False Claims Act Filing Under Seal (31 U.S.C. § 3730(b)(2))",
        "Summary/Notes": "Staged under-seal complaint transmittal ($6,094,847 LMIHAF toxic site conversion at 17631 Cameron Ln)."
    },
    {
        "Date": "Oct 18, 2026",
        "Sector": "Public Sector",
        "Entity/Recipient": "FBI Los Angeles Field Office (Public Corruption Squad)",
        "Subject/Topic": "Criminal Referral (18 U.S.C. § 666 / Wire Fraud / Civil RICO)",
        "Summary/Notes": "Referral of insider self-dealing, fraudulent land conversion, and federal-fund theft at HBNC."
    },
    {
        "Date": "Oct 18, 2026",
        "Sector": "Public Sector",
        "Entity/Recipient": "HUD OIG Hotline (oig.hotline@hud.gov)",
        "Subject/Topic": "False Claims Act Disclosure (LMIHAF / CDBG-CV / ESG-CV diversion)",
        "Summary/Notes": "Disclosure regarding $6.09M LMIHAF disbursement on Cr(VI) contaminated site concealed by Case #20IC002."
    },
    {
        "Date": "Oct 18, 2026",
        "Sector": "Public Sector",
        "Entity/Recipient": "EPA OIG Hotline (oig_hotline@epa.gov)",
        "Subject/Topic": "Environmental Crimes & False Statements (RCRA / 42 U.S.C. § 6928)",
        "Summary/Notes": "Referral detailing unpermitted Sprung structure, unsealed drinking well W-4150, and 1,085 CY toxic soil export."
    },
    {
        "Date": "Oct 18, 2026",
        "Sector": "Public Sector",
        "Entity/Recipient": "SEC Whistleblower Office (TCR Portal)",
        "Subject/Topic": "Municipal Securities Fraud / Disclosure Omission (15 U.S.C. § 78j(b))",
        "Summary/Notes": "Whistleblower submission on undisclosed environmental liabilities and fake addresses affecting municipal bonds."
    },
    {
        "Date": "Oct 18, 2026",
        "Sector": "Public Sector",
        "Entity/Recipient": "California State Auditor (Whistleblower Hotline)",
        "Subject/Topic": "State Fund Diversion & HHAP Audit Request",
        "Summary/Notes": "Referral for audit of HHAP and state funding passed through County of Orange to Mercy House at HBNC."
    },
    {
        "Date": "Oct 18, 2026",
        "Sector": "Public Sector",
        "Entity/Recipient": "California Attorney General (Public Rights Division)",
        "Subject/Topic": "Government Code § 1090 Void-Ab-Initio / Thomson v. Call Disgorgement",
        "Summary/Notes": "Demand for statutory disgorgement and judicial nullification of tainted municipal contracts."
    }
]

for s in staged_entries:
    clean_records.append(s)

print(f"Final total master records: {len(clean_records)}")

# Write to fully updated CSV
output_csv = "/mnt/c/Amd949609_Antigravity_v1/summaries/MASTER_OUTREACH_EFFORTS_FULLY_UPDATED.csv"
with open(output_csv, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for rec in clean_records:
        writer.writerow(rec)

# Write to formatted Markdown for review and import
output_md = "/mnt/c/Amd949609_Antigravity_v1/summaries/MASTER_OUTREACH_EFFORTS_FULLY_UPDATED.md"
with open(output_md, "w", encoding="utf-8") as f:
    f.write("# Summary of Outreach Efforts (2021–Present) — Master Updated Ledger\n\n")
    f.write(f"**Source Sheet:** https://docs.google.com/spreadsheets/d/1GiNM335Vn4T7WgK6fdmYDluvwY8dD23loQbjClvViDk/edit?pli=1&gid=0#gid=0\n")
    f.write(f"**Total Consolidated Records:** {len(clean_records)}\n\n")
    f.write("| Date | Sector | Entity / Recipient | Subject / Topic | Summary / Notes |\n")
    f.write("|---|---|---|---|---|\n")
    for rec in clean_records:
        date_esc = rec['Date'].replace('|', '/')
        sec_esc = rec['Sector'].replace('|', '/')
        ent_esc = rec['Entity/Recipient'].replace('|', '/')
        sub_esc = rec['Subject/Topic'].replace('|', '/')
        sum_esc = rec['Summary/Notes'].replace('|', '/')
        f.write(f"| {date_esc} | {sec_esc} | {ent_esc} | {sub_esc} | {sum_esc} |\n")

print(f"Exported clean files:\n- {output_csv}\n- {output_md}")
