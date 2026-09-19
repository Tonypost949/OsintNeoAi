"""run_lightbox_batch_audit.py — Multi-API LightBox RE Batch Audit Engine
Executes Parcels, Assessments, Structures, Zoning, and EDR Environmental APIs against all targets,
including GPS coordinate-based spatial audits for Nevada / MGM Grand / Desert parcels.
"""

import os
import json
import time
from pathlib import Path
from lightbox_edr_engine import LightBoxEDREngine

# Target Audits across Address & Exact GPS Coordinates
PRIMARY_AUDIT_TARGETS = [
    {"name": "Vagabond Inn / Casa Aliento (Mercy House CHDO)", "address": "17642 Beach Blvd, Huntington Beach, CA 92647", "lat": 33.7088, "lon": -117.9890},
    {"name": "Cameron Lane Property Hub", "address": "17631 Cameron Ln, Huntington Beach, CA 92647", "lat": 33.7081, "lon": -117.9902},
    {"name": "Beach Blvd Commercial Parcel", "address": "19102 Beach Blvd, Huntington Beach, CA 92648", "lat": 33.6845, "lon": -117.9895},
    {"name": "Garden Grove Blvd Asset", "address": "13252 Garden Grove Blvd, Garden Grove, CA 92843", "lat": 33.7745, "lon": -117.9056},
    {"name": "Huntington Beach Civic Center", "address": "2000 Main St, Huntington Beach, CA 92648", "lat": 33.6603, "lon": -117.9992},
    {"name": "Fair Drive County Hub", "address": "88 Fair Dr, Costa Mesa, CA 92626", "lat": 33.6644, "lon": -117.8967},
    {"name": "MGM Grand Hotel & Casino (Nevada Hub)", "address": "3799 S Las Vegas Blvd, Las Vegas, NV 89109", "lat": 36.1026, "lon": -115.1703},
    {"name": "Apex Desert Industrial Corridor (Nevada)", "address": "Apex Desert Parcel, Clark County, NV", "lat": 36.3150, "lon": -114.9200},
    {"name": "Nye County Desert Mining / Testing Site", "address": "Beatty Corridor, Nye County, NV", "lat": 36.9092, "lon": -116.7547},
    {"name": "Storey County / Tahoe-Reno Industrial", "address": "USA Pkwy, Sparks, NV 89437", "lat": 39.5296, "lon": -119.8138}
]

def main():
    print("=" * 75)
    print("🏢 LIGHTBOX RE & EDR MULTI-API BATCH AUDIT ENGINE")
    print("   [+] Integrated Address Geocoding + Exact GPS Desert Spatial Audits")
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
        lat = target.get("lat")
        lon = target.get("lon")
        print(f"[{i}/{len(PRIMARY_AUDIT_TARGETS)}] Auditing: {site_name}")
        print(f"    Address / Description: '{addr}'")
        print(f"    Exact GPS Coordinates: ({lat}, {lon})")
        
        site_result = {
            "target_name": site_name,
            "address": addr,
            "gps_coordinates": {"latitude": lat, "longitude": lon},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "endpoints": {}
        }

        # 1. Parcels by Address API
        print("    --> Querying LightBox Parcels API...")
        res_parcel = engine.search_parcel_by_address(addr)
        site_result["endpoints"]["parcels_address"] = res_parcel
        
        # 2. Spatial Radius Parcels API (using GPS Coordinates)
        if lat and lon:
            print("    --> Querying Spatial Radius Parcels API (GPS)...")
            res_radius = engine.search_parcels_by_radius(lat, lon, radius_meters=500)
            site_result["endpoints"]["parcels_radius_gps"] = res_radius
            
            print("    --> Querying EDR Contaminated Sites by Radius (GPS)...")
            res_edr_radius = engine.search_edr_sites_by_radius(lat, lon, radius_miles=0.5)
            site_result["endpoints"]["edr_sites_radius_gps"] = res_edr_radius

        # 3. EDR Environmental Reports API
        print("    --> Querying EDR Environmental Reports API...")
        res_edr = engine.fetch_edr_environmental_report(addr)
        site_result["endpoints"]["edr_environmental"] = res_edr

        # 4. Local EDR Database Matches
        search_key = addr.split(",")[0]
        local_matches = engine.search_edr_records(search_key)
        if not local_matches and "NV" in addr or "Nevada" in addr or "MGM" in addr:
            local_matches = engine.search_edr_records("Nevada") or engine.search_edr_records("Vegas")
            
        site_result["local_edr_matches"] = len(local_matches)
        site_result["local_edr_records"] = local_matches[:5]
        print(f"    --> Local Historical EDR Matches: {len(local_matches)}")
        
        master_results.append(site_result)
        time.sleep(0.3)

    # Save JSON Master Report
    json_path = output_dir / "LIGHTBOX_AUDIT_OUTPUT_MASTER.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(master_results, f, indent=2)
    print(f"\n[+] Master JSON written: {json_path}")

    # Generate Markdown Summary Dossier
    md_lines = [
        "# 🏢 LightBox RE & EDR Multi-API Forensic Audit Dossier",
        f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Targets Audited:** {len(PRIMARY_AUDIT_TARGETS)} (California + Nevada Desert Hubs)",
        "",
        "## I. Target Audit Results Matrix (Address + Spatial GPS Coordinates)",
        "",
        "| Target Name | Address / GPS | Parcels API | GPS Radius API | EDR Environmental | Local EDR Matches |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for r in master_results:
        p_status = r["endpoints"].get("parcels_address", {}).get("status_code", "N/A")
        r_status = r["endpoints"].get("parcels_radius_gps", {}).get("status_code", "N/A")
        e_status = r["endpoints"].get("edr_environmental", {}).get("status_code", "N/A")
        gps_str = f"{r['gps_coordinates']['latitude']}, {r['gps_coordinates']['longitude']}"
        md_lines.append(f"| **{r['target_name']}** | `{r['address']}`<br>📍 `{gps_str}` | HTTP {p_status} | HTTP {r_status} | HTTP {e_status} | **{r['local_edr_matches']} records** |")

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
    print("✅ LIGHTBOX & NEVADA DESERT GPS BATCH AUDIT COMPLETE")
    print("=" * 75)

if __name__ == "__main__":
    main()
