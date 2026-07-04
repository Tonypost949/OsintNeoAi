import requests
import json
from google.cloud import bigquery

# Initialize BigQuery Client (using Application Default Credentials)
bq_client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
DATASET_ID = "project-743aab84-f9a5-4ec7-954.ai_sandbox"

def ingest_arcgis_layer(layer_url, table_name, max_features=2000):
    """
    Downloads GeoJSON from an ArcGIS REST endpoint and loads it into BigQuery.
    """
    print(f"Downloading ArcGIS layer from {layer_url}...")
    
    # Query parameters for ArcGIS REST API
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "resultRecordCount": max_features
    }
    
    res = requests.get(f"{layer_url}/query", params=params)
    res.raise_for_status()
    geojson_data = res.json()
    
    features = geojson_data.get("features", [])
    print(f"Downloaded {len(features)} features.")
    if not features:
        return
        
    # Flatten GeoJSON for BigQuery insertion
    rows_to_insert = []
    for f in features:
        props = f.get("properties", {})
        geom = f.get("geometry", {})
        
        # Create a flattened row with a geometry JSON string and sanitize column names
        row = {}
        if props:
            for k, v in props.items():
                safe_k = k.replace('.', '_').replace('(', '').replace(')', '').replace(' ', '_')
                row[safe_k] = v
        row["geometry_json"] = json.dumps(geom)
        rows_to_insert.append(row)
    
    # Normally we would dynamically generate a schema, 
    # but for this OSINT Sandbox we can use BigQuery's autodetect by saving to newline-delimited JSON and running a load job.
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as tmp:
        for row in rows_to_insert:
            tmp.write(json.dumps(row) + '\n')
        tmp_path = tmp.name
        
    table_id = f"{DATASET_ID}.{table_name}"
    print(f"Loading data into {table_id}...")
    
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )
    
    with open(tmp_path, "rb") as source_file:
        job = bq_client.load_table_from_file(source_file, table_id, job_config=job_config)
    
    job.result()  # Waits for the job to complete
    
    print(f"[+] Successfully ingested {job.output_rows} rows into {table_id}")
    import os
    os.remove(tmp_path)

if __name__ == "__main__":
    # Example Huntington Beach Layer URLs (adjust the exact layer ID as needed)
    # The user's AI can dynamically execute this with the correct layers!
    target_layers = {
        "hb_environmental_sites": "https://gis.huntingtonbeachca.gov/arcgis/rest/services/Public_Works/Environmental/MapServer/0",
        "hb_zoning_parcels": "https://gis.huntingtonbeachca.gov/arcgis/rest/services/Public_Works/Zoning/MapServer/0"
    }
    
    for table_name, url in target_layers.items():
        try:
            ingest_arcgis_layer(url, table_name)
        except Exception as e:
            print(f"[!] Failed to ingest {table_name}: {e}")
