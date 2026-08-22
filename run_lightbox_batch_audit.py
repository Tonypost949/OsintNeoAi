"""run_lightbox_batch_audit.py — Multi-API LightBox RE Batch Audit Engine
Executes Parcels, Assessments, Structures, Zoning, and EDR Environmental APIs against all targets.
"""

import os
import json
import time
from pathlib import Path
from lightbox_edr_engine import LightBoxEDREngine

# Target Addresses to Audit across LightBox RE APIs
PRIMARY_AUDIT_TARGETS = [
    {"name": "Vagabond Inn / Casa Aliento (Mercy House CHDO)", "address": "17642 Beach Blvd, Huntington Beach, CA 92647"},
    {"name": "Cameron Lane Property Hub", "address": "17631 Cameron Ln, Huntington Beach, CA 92647"},
    {"name": "Beach Blvd Commercial Parcel", "address": "19102 Beach Blvd, Huntington Beach, CA 92648"},
    {"name": "Garden Grove Blvd Asset", "address": "13252 Garden Grove Blvd, Garden Grove, CA 92843"},
    {"name": "Huntington Beach Civic Center", "address": "2000 Main St, Huntington Beach, CA 92648"},
    {"name": "Fair Drive County Hub", "address": "88 Fair Dr, Costa Mesa, CA 92626"}
]

def main():
    print("=" * 75)
    print("🏢 LIGHTBOX RE & EDR MULTI-API BATCH AUDIT ENGINE")
    print("=" * 75)
    
    engine = LightBoxEDREngine()
    stats = engine.get_summary_stats()
    print(f"[*] Loaded Local EDR Records: {stats['total_cached_records']}")
    print(f"[*] Live API Active: {stats['live_api_active']}")
    print(f"[*] Target Audit Sites: {len(PRIMARY_AUDIT_TARGETS)}\n")

    output_dir = Path("reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    master_results = []
    
    for i, target in enumerate(PRIMARY_AUDIT_TARGETS, 1):
        site_name = target["name"]
        addr = target["address"]
        print(f"[{i}/{len(PRIMARY_AUDIT_TARGETS)}] Auditing: {site_name}")
        print(f"    Address: '{addr}'")
        
        site_result = {
            "target_name": site_name,
            "address": addr,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "endpoints": {}
        }

        # 1. Parcels by Address API
        print("    --> Querying LightBox Parcels API...")
        res_parcel = engine.search_parcel_by_address(addr)
        site_result["endpoints"]["parcels"] = res_parcel
        parcel_id = None
        if res_parcel.get("status_code") == 200 and isinstance(res_parcel.get("data"), dict):
            parcels_list = res_parcel.get("data", {}).get("parcels", [])
            if parcels_list:
                parcel_id = parcels_list[0].get("id")
                print(f"        [+] Found Parcel ID: {parcel_id}")

        # 2. EDR Environmental Reports API
        print("    --> Querying EDR Environmental Reports API...")
        res_edr = engine.fetch_edr_environmental_report(addr)
        site_result["endpoints"]["edr_environmental"] = res_edr

        # 3. Assessment & Property Tax API (if parcel_id or address)
        if parcel_id:
            print("    --> Querying Assessments API...")
            res_assess = engine.get_assessment_data(parcel_id)
            site_result["endpoints"]["assessments"] = res_assess

            print("    --> Querying Structures API...")
            res_struct = engine.get_structure_data(parcel_id)
            site_result["endpoints"]["structures"] = res_struct

            print("    --> Querying Zoning API...")
            res_zoning = engine.get_zoning_data(parcel_id)
            site_result["endpoints"]["zoning"] = res_zoning

        # 4. Local EDR Database Matches
        local_matches = engine.search_edr_records(addr.split(",")[0])
        site_result["local_edr_matches"] = len(local_matches)
        site_result["local_edr_records"] = local_matches[:5]
        print(f"    --> Local Historical EDR Matches: {len(local_matches)}")
        
        master_results.append(site_result)
        time.sleep(0.5)

    # Save JSON Master Report
    json_path = output_dir / "LIGHTBOX_AUDIT_OUTPUT_MASTER.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(master_results, f, indent=2)
    print(f"\n[+] Master JSON written: {json_path}")

    # Generate Markdown Summary Dossier
    md_lines = [
        "# 🏢 LightBox RE & EDR Multi-API Forensic Audit Dossier",
        f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Targets Audited:** {len(PRIMARY_AUDIT_TARGETS)}",
        "",
        "## I. Target Audit Results Matrix",
        "",
        "| Target Name | Address | Parcels API | EDR Environmental | Local EDR Matches |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    for r in master_results:
        p_status = r["endpoints"].get("parcels", {}).get("status_code", "N/A")
        e_status = r["endpoints"].get("edr_environmental", {}).get("status_code", "N/A")
        md_lines.append(f"| **{r['target_name']}** | `{r['address']}` | HTTP {p_status} | HTTP {e_status} | **{r['local_edr_matches']} records** |")

    md_lines.extend([
        "",
        "## II. Historical EDR Environmental Site Disclosures",
        ""
    ])
    for r in master_results:
        if r["local_edr_records"]:
            md_lines.append(f"### 📍 {r['target_name']}")
            for rec in r["local_edr_records"]:
                md_lines.append(f"- **Source File:** `{rec.get('file', 'N/A')}`")
                md_lines.append(f"  *Cover Address:* `{rec.get('cover_address', 'N/A')}`")
                md_lines.append(f"  *Physical Location:* `{rec.get('real_physical_location', 'N/A')}`")
                md_lines.append("")

    md_path = output_dir / "LIGHTBOX_PARCEL_AUDIT_REPORT.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[+] Markdown Summary written: {md_path}")
    print("\n" + "=" * 75)
    print("✅ LIGHTBOX BATCH AUDIT COMPLETE")
    print("=" * 75)

if __name__ == "__main__":
    main()
