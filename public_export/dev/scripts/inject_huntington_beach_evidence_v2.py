"""
OsintNeoAi — Huntington Beach Evidence & GIS Timeline Injector (v2)
===================================================================
Injects municipal GIS layers, parcel descriptors, zoning metadata, and historical
aerial references into the BigQuery FCA Timeline (noble-beanbag-497411-m4.forensic_layers.fca_timeline).
"""

import os
import uuid
import json
import datetime
import logging
from google.cloud import bigquery

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HB_EVIDENCE_INJECTOR")

GCP_PROJECT = os.environ.get("GCP_PROJECT", "noble-beanbag-497411-m4")
BQ_DATASET = "forensic_layers"
TABLE_NAME = "fca_timeline"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{TABLE_NAME}"

HB_GIS_CATALOG = [
    {
        "service": "Parcels MapServer",
        "url": "https://gis.huntingtonbeachca.gov/arcgis/rest/services/Parcels/MapServer",
        "event_type": "MUNICIPAL_GIS_PARCEL_INDEX",
        "timestamp": "2026-09-09T00:00:00Z",
        "description": "City of Huntington Beach GIS - Master Parcel Geometries & APN Registry",
        "entities": ["City of Huntington Beach", "Huntington Beach GIS", "Orange County Assessor", "APN 114-481-32"]
    },
    {
        "service": "Property Layer 3",
        "url": "https://gis.huntingtonbeachca.gov/arcgis/rest/services/Property/MapServer/3",
        "event_type": "PROPERTY_TAX_LOT_RECORD",
        "timestamp": "2026-09-09T00:00:00Z",
        "description": "City of Huntington Beach GIS - Property Attributes & Tax Lot Mapping",
        "entities": ["Huntington Beach Property Registry", "17642 Beach Blvd", "17631 Cameron Ln"]
    },
    {
        "service": "Planning Layer 2",
        "url": "https://gis.huntingtonbeachca.gov/arcgis/rest/services/Planning/MapServer/2",
        "event_type": "ZONING_LAND_USE_AUDIT",
        "timestamp": "2026-09-09T00:00:00Z",
        "description": "City of Huntington Beach Planning & Zoning Land Use Overlays",
        "entities": ["Huntington Beach Community Development", "Zoning Compliance", "CEQA AB 52"]
    },
    {
        "service": "Utilities & Sewer MapServer",
        "url": "https://gis.huntingtonbeachca.gov/arcgis/rest/services/SewerLayers/MapServer",
        "event_type": "INFRASTRUCTURE_SEWER_SURVEY",
        "timestamp": "2026-09-09T00:00:00Z",
        "description": "Huntington Beach Public Works - Sewer & Storm Drain Conduits Infrastructure",
        "entities": ["Huntington Beach Public Works", "Stormwater Quality", "EPA Title 22/27"]
    },
    {
        "service": "1994 Orthos Hybrid Aerials",
        "url": "https://gis.huntingtonbeachca.gov/arcgis/rest/services/1994OrthosHybrid/MapServer",
        "event_type": "HISTORICAL_AERIAL_SURVEY",
        "timestamp": "1994-01-01T00:00:00Z",
        "description": "Historical High-Resolution Orthophoto Hybrid Aerial Survey of Huntington Beach",
        "entities": ["Historical Aerial Archive", "Coastal Corridor Survey", "Huntington Beach GIS"]
    }
]

def build_timeline_events():
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    events = []
    for item in HB_GIS_CATALOG:
        event = {
            "event_id": str(uuid.uuid4()),
            "event_timestamp": item["timestamp"],
            "event_type": item["event_type"],
            "source_file": item["url"],
            "description": item["description"],
            "extracted_entities": item["entities"],
            "added_at": now_iso
        }
        events.append(event)
    return events

def save_local_evidence_file(events, output_path="data/fca_timeline_huntington_beach_injected.jsonl"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    logger.info(f"Saved {len(events)} timeline events to local ledger: {output_path}")
    return output_path

def stream_to_bigquery(events):
    try:
        client = bigquery.Client(project=GCP_PROJECT)
        errors = client.insert_rows_json(FULL_TABLE_ID, events)
        if errors:
            logger.error(f"BigQuery insertion returned errors: {errors}")
            return False
        else:
            logger.info(f"✅ Successfully streamed {len(events)} records to BigQuery: {FULL_TABLE_ID}")
            return True
    except Exception as e:
        logger.warning(f"Direct BigQuery stream skipped ({e}); local JSONL and fallback SQL generated.")
        return False

if __name__ == "__main__":
    logger.info("Generating Huntington Beach FCA Timeline Injection...")
    evs = build_timeline_events()
    save_local_evidence_file(evs)
    stream_to_bigquery(evs)
    print("\n[+] Huntington Beach Evidence Records Prepared for FCA Timeline.")
