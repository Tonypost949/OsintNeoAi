import sqlite3
import json
import os
import re

def compile_homeless_timeline():
    print("[+] Compiling Master Timeline: 2021 to Present Day (2026)...")
    
    db_path = r"C:\OsintNeoAi\osint_vector_index.db"
    manifest_path = r"C:\OsintNeoAi\EVIDENCE_LOCKER_SHA256_MANIFEST.json"
    
    timeline_events = []
    
    # 1. Vector Database Parsing
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM osint_nodes LIMIT 2000;")
        rows = cur.fetchall()
        for r in rows:
            r_str = str(r)
            r_lower = r_str.lower()
            if any(k in r_lower for k in ["2021", "2022", "2023", "2024", "2025", "2026", "eviction", "homeless", "shelter", "housing", "retaliation"]):
                # Extract year
                years = re.findall(r'202[1-6]', r_str)
                year = years[0] if years else "2021-2026"
                timeline_events.append({
                    "year": year,
                    "source": "Vector Node Database",
                    "details": r_str[:200]
                })
        conn.close()

    # 2. Evidence Locker Manifest Parsing
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            files = json.load(f)
            for item in files:
                item_str = str(item)
                item_lower = item_str.lower()
                if any(k in item_lower for k in ["2021", "2022", "2023", "2024", "2025", "2026", "eviction", "housing", "retaliation", "ocr", "hit"]):
                    years = re.findall(r'202[1-6]', item_str)
                    year = years[0] if years else "Evidence Record"
                    timeline_events.append({
                        "year": year,
                        "source": "Physical Evidence Locker Manifest",
                        "details": item_str
                    })

    # Sort events by year
    timeline_events.sort(key=lambda x: str(x["year"]))

    # Output Markdown Report
    md_path = r"C:\OsintNeoAi\TIMELINE_2021_TO_PRESENT_DAY.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 📅 MASTER CHRONOLOGICAL TIMELINE: 2021 TO PRESENT DAY (2026)\n\n")
        f.write("**Subject:** Unlawful Retaliatory Eviction, Housing Deprivation & Evidentiary Chain of Custody\n")
        f.write(f"**Total Events & Evidence Records Compiled:** `{len(timeline_events)}`\n\n")
        f.write("---\n\n")

        # Group by Year
        years_group = {}
        for ev in timeline_events:
            y = ev["year"]
            if y not in years_group:
                years_group[y] = []
            years_group[y].append(ev)

        for y in sorted(years_group.keys()):
            f.write(f"## 📌 YEAR / ANCHOR: {y}\n")
            f.write(f"**Total Records in Anchor:** {len(years_group[y])}\n\n")
            for item in years_group[y][:15]: # Top 15 key entries per year
                f.write(f"- **[{item['source']}]** {item['details']}\n")
            if len(years_group[y]) > 15:
                f.write(f"- *...and {len(years_group[y]) - 15} additional verified records*\n")
            f.write("\n")

    print(f"[+] Timeline compiled with {len(timeline_events)} records at: {md_path}")

if __name__ == "__main__":
    compile_homeless_timeline()
