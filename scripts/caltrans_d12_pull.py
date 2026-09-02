#!/usr/bin/env python3
"""
scripts/caltrans_d12_pull.py
============================
Automated extraction pipeline for Caltrans District 12 (Orange County) 
live CCTV cameras via the State Highway Network ArcGIS REST API.

Outputs:
- C:\\OsintNeoAi\\evidence\\caltrans_d12_cctv.geojson
- C:\\OsintNeoAi\\viewers\\gods-eye-view\\public\\caltrans_d12_cctv.geojson
- C:\\OsintNeoAi\\opencode_work\\caltrans_d12_cctv.geojson
"""

import os
import json
import requests
import shutil

try:
    from rich.console import Console
    from rich.progress import track
    console = Console()
except ImportError:
    class DummyConsole:
        def print(self, *args, **kwargs):
            clean_str = str(args[0]) if args else ""
            import re
            clean_str = re.sub(r'\[.*?\]', '', clean_str)
            print(clean_str)
        def status(self, msg):
            class StatusContext:
                def __enter__(self): return self
                def __exit__(self, *a): pass
            return StatusContext()
    console = DummyConsole()
    def track(sequence, description=""):
        return sequence

from pathlib import Path

THIS_FILE = Path(__file__).resolve()
BASE_DIR_PATH = THIS_FILE.parents[1] if THIS_FILE.parents[1].name != "scripts" else THIS_FILE.parents[1]
if not (BASE_DIR_PATH / "evidence").exists():
    for cand in [Path("/home/site/wwwroot"), Path("C:/OsintNeoAi"), Path.cwd()]:
        if (cand / "evidence").exists():
            BASE_DIR_PATH = cand
            break

BASE_DIR = str(BASE_DIR_PATH)
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")
GEOJSON_OUT = os.path.join(EVIDENCE_DIR, "caltrans_d12_cctv.geojson")
VIEWER_DIR = os.path.join(BASE_DIR, "viewers", "gods-eye-view", "public")
OPENCODE_DIR = os.path.join(BASE_DIR, "opencode_work")

def fetch_caltrans_cctv():
    console.print("[bold cyan]🚀 Initializing Caltrans District 12 (Orange County) CCTV Pipeline...[/bold cyan]")
    
    # ArcGIS REST API endpoint for Caltrans CCTV FeatureServer
    api_url = (
        "https://caltrans-gis.dot.ca.gov/arcgis/rest/services/"
        "CHhighway/CCTV/FeatureServer/0/query"
    )
    
    # Query parameters targeting District 12 (Orange County)
    params = {
        "where": "district=12", 
        "outFields": "*",
        "outSR": "4326",  
        "f": "geojson"
    }

    try:
        console.print("[bold green]Querying State Highway Network (ArcGIS REST API)...[/bold green]")
        response = requests.get(api_url, params=params, timeout=25)
        response.raise_for_status()
        data = response.json()
            
        features = data.get("features", [])
        
        if not features:
            console.print("[bold red]⚠️ No cameras returned for District 12. Check API status.[/bold red]")
            return

        console.print(f"[bold green]✅ Successfully extracted {len(features)} active traffic cameras from Caltrans D12.[/bold green]")
        
        processed_features = []
        for feature in track(features, description="[cyan]Formatting tactical feeds for spatial ingestion...[/cyan]"):
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            
            # Reconstruct properties to include tactical metadata for God's Eye View HUD & MapLibre
            hud_props = {
                "object_id": props.get("OBJECTID"),
                "entity_name": props.get("locationName", "Unknown Location"),
                "nearby_place": props.get("nearbyPlace", ""),
                "county": props.get("county", "Orange"),
                "district": props.get("district", 12),
                "route": props.get("route", ""),
                "direction": props.get("direction", ""),
                "elevation_ft": props.get("elevation", 0),
                "postmile": props.get("postmile"),
                "image_url": props.get("currentImageURL", ""),
                "stream_url": props.get("streamingVideoURL", ""),
                "update_freq_sec": props.get("currentImageUpdateFrequency", "5"),
                "in_service": str(props.get("inService", "True")).lower() == "true",
                "latitude": props.get("latitude"),
                "longitude": props.get("longitude"),
                "threat_score": 0,
                "category": "CCTV_FEED"
            }
            
            processed_features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": hud_props
            })

        final_geojson = {
            "type": "FeatureCollection",
            "metadata": {
                "source": "Caltrans District 12 ArcGIS FeatureServer",
                "total_cameras": len(processed_features),
                "region": "Orange County, CA",
                "jurisdiction": "Caltrans D12"
            },
            "features": processed_features
        }

        # Ensure destination directories exist
        os.makedirs(EVIDENCE_DIR, exist_ok=True)
        os.makedirs(OPENCODE_DIR, exist_ok=True)
        if os.path.exists(os.path.dirname(VIEWER_DIR)):
            os.makedirs(VIEWER_DIR, exist_ok=True)
        
        # 1. Export primary evidence GeoJSON
        with open(GEOJSON_OUT, "w", encoding="utf-8") as f:
            json.dump(final_geojson, f, indent=2)
        console.print(f"[bold green]✅ Primary Evidence GeoJSON generated:[/bold green] {GEOJSON_OUT}")

        # 2. Sync to opencode_work/ for simple map server
        opencode_path = os.path.join(OPENCODE_DIR, "caltrans_d12_cctv.geojson")
        with open(opencode_path, "w", encoding="utf-8") as f:
            json.dump(final_geojson, f, indent=2)
        console.print(f"[bold green]✅ Copied to Opencode Work layer:[/bold green] {opencode_path}")

        # 3. Sync to viewers/gods-eye-view/public/ if available
        if os.path.exists(VIEWER_DIR):
            viewer_geojson = os.path.join(VIEWER_DIR, "caltrans_d12_cctv.geojson")
            with open(viewer_geojson, "w", encoding="utf-8") as f:
                json.dump(final_geojson, f, indent=2)
            console.print(f"[bold green]✅ Synced to God's Eye View public directory:[/bold green] {viewer_geojson}")
            
        console.print("\n[bold yellow]📡 Live Feeds Ready for 3D Ingestion into God's Eye View & Port 5052 / Port 10000 Maps Hub.[/bold yellow]")

    except Exception as e:
        console.print(f"[bold red]❌ CCTV Extraction Process failed:[/bold red] {e}")

if __name__ == "__main__":
    fetch_caltrans_cctv()
