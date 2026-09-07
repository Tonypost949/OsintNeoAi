"""
load_hb_parcels_to_bigquery.py
Loads official City of Huntington Beach GIS datasets into BigQuery forensic_layers:
1. hb_city_owned_properties (719 city-owned parcels with APN, acreage, fiscal year)
2. hb_target_parcels (HBNC 167-472-08/09, Onni 165-364-16, Taylor DRT 153-091-27, Shady Harbor 023-262-35)
"""
import os
import json
import tempfile
from google.cloud import bigquery

PROJECT = "noble-beanbag-497411-m4"
DATASET = "ai_sandbox"

client = bigquery.Client(project=PROJECT)

def sanitize_key(k: str) -> str:
    return (k.replace('.', '_')
            .replace('(', '_')
            .replace(')', '')
            .replace(' ', '_')
            .replace('-', '_'))

def load_json_to_bq(rows, table_name):
    table_id = f"{PROJECT}.{DATASET}.{table_name}"
    print(f"Loading {len(rows)} rows into {table_id}...")
    
    sanitized_rows = []
    for r in rows:
        clean_row = {}
        for k, v in r.items():
            clean_row[sanitize_key(k)] = v
        sanitized_rows.append(clean_row)
        
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl', encoding='utf-8') as tmp:
        for r in sanitized_rows:
            tmp.write(json.dumps(r) + '\n')
        tmp_path = tmp.name

    try:
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        with open(tmp_path, "rb") as f:
            job = client.load_table_from_file(f, table_id, job_config=job_config)
        job.result()
        print(f"[+] Successfully loaded {job.output_rows} rows into {table_id}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def main():
    # 1. Load City Owned Properties
    city_props_path = r"c:\OsintNeoAi\evidence\hb_city_owned_properties_719.json"
    if os.path.exists(city_props_path):
        with open(city_props_path, "r", encoding="utf-8") as f:
            city_props = json.load(f)
        load_json_to_bq(city_props, "hb_city_owned_properties")

    # 2. Load Target Parcels (HBNC + Corridor)
    target_rows = []
    
    # HBNC parcels
    hbnc_path = r"c:\OsintNeoAi\evidence\hbnc_parcels_167_472_08_09.json"
    if os.path.exists(hbnc_path):
        with open(hbnc_path, "r", encoding="utf-8") as f:
            hbnc_data = json.load(f)
            for feat in hbnc_data.get("features", []):
                attrs = dict(feat.get("attributes", {}))
                attrs["geometry_json"] = json.dumps(feat.get("geometry", {}))
                attrs["investigation_target"] = "HBNC_NAVIGATION_CENTER"
                target_rows.append(attrs)

    # Corridor parcels (17011 Beach Onni, 19900 Beach Taylor DRT, 19331 Shady)
    corridor_path = r"c:\OsintNeoAi\evidence\target_parcels_corridor.json"
    if os.path.exists(corridor_path):
        with open(corridor_path, "r", encoding="utf-8") as f:
            corridor_data = json.load(f)
            for feat in corridor_data:
                attrs = dict(feat.get("attributes", {}))
                attrs["geometry_json"] = json.dumps(feat.get("geometry", {}))
                apn = attrs.get("DATA.Parcels.APN", "")
                if "165-364-16" in apn:
                    attrs["investigation_target"] = "ONNI_HUNTINGTON_BEACH_CORRIDOR"
                elif "153-091-27" in apn:
                    attrs["investigation_target"] = "TAYLOR_DRT_BEACH_CORRIDOR"
                elif "023-262-35" in apn:
                    attrs["investigation_target"] = "SHADY_HARBOR_RADIUS_CENTER"
                else:
                    attrs["investigation_target"] = "CORRIDOR_TARGET"
                target_rows.append(attrs)

    if target_rows:
        load_json_to_bq(target_rows, "hb_target_parcels")

if __name__ == "__main__":
    main()
