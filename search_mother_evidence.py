import json
import os

def search_mother_evidence():
    manifest_path = r"C:\OsintNeoAi\EVIDENCE_LOCKER_SHA256_MANIFEST.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            mother_evidence = []
            keywords = ["mom", "mother", "disabled", "disability", "injury", "injured", "fall", "cps", "elder", "family", "woodbridge", "eviction"]
            
            for item in data:
                item_str = json.dumps(item).lower()
                if any(k in item_str for k in keywords):
                    mother_evidence.append(item)
            
            print(f"[+] Total Evidence Files Matched for Disabled Mother / Family Eviction & Injury: {len(mother_evidence)}")
            output_file = r"C:\OsintNeoAi\DISABLED_MOTHER_INJURY_AND_EVICTION_EVIDENCE_INDEX.json"
            with open(output_file, "w", encoding="utf-8") as out:
                json.dump(mother_evidence, out, indent=2)
            print(f"[+] Index written to: {output_file}")

            # Generate Human Readable Case Brief
            md_file = r"C:\OsintNeoAi\DISABLED_MOTHER_INJURY_AND_EVICTION_CASE_BRIEF.md"
            with open(md_file, "w", encoding="utf-8") as md:
                md.write("# ⚖️ SPECIAL COMPLAINT DOSSIER: INJURY TO DISABLED MOTHER & RETALIATORY EVICTION\n\n")
                md.write(f"**Subject:** Unlawful Eviction of Disabled Parent, Physical Injury & HUD Fair Housing Discrimination\n")
                md.write(f"**Verified Evidence Files Matched:** `{len(mother_evidence)}` records\n\n")
                md.write("### 📜 Governing Federal & State Legal Statutory Violations:\n")
                md.write("1. **Americans with Disabilities Act (ADA - 42 U.S.C. § 12182):** Failure to provide reasonable accommodation for disabled co-resident.\n")
                md.write("2. **Fair Housing Act (42 U.S.C. § 3604(f)):** Discrimination against disabled individuals in housing and retaliatory eviction.\n")
                md.write("3. **Elder Abuse & Dependent Adult Civil Protection Act (Cal. Welf. & Inst. Code § 15657):** Physical harm, neglect, and displacement of disabled elder.\n")
                md.write("4. **California Civil Code § 1942.5:** Retaliatory eviction causing physical injury and displacement.\n\n")
                md.write("### 📁 Primary Evidentiary File Sample:\n")
                for item in mother_evidence[:15]:
                    md.write(f"- **File:** `{item.get('path', '')}` (SHA-256: `{item.get('sha256', '')}`)\n")

if __name__ == "__main__":
    search_mother_evidence()
