
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(r"C:\OsintNeoAi")

def build_neo_gis_engine():
    catalog_path = PROJECT_ROOT / "data" / "hb_gis_42_services_master.json"
    if not catalog_path.exists():
        print("Error: hb_gis_42_services_master.json not found")
        return

    with open(catalog_path, "r", encoding="utf-8") as f:
        gis_catalog = json.load(f)

    categories = {
        "CADASTRAL_LAND_TENURE": ["Parcels", "Property", "Planning", "Grids", "FindAddressParcel"],
        "HISTORICAL_AERIAL_SURVEILLANCE": ["1960sAerials", "1970sAerials", "1980sAerials", "1990sAerials", "1994OrthosHybrid", "2001OrthosHybrid", "2006OrthosHybrid", "2010OrthosHybrid", "2012OrthosHybrid", "2014OrthosHybrid", "2015OrthosHybrid", "2021Orthos"],
        "CRITICAL_INFRASTRUCTURE_UTILITIES": ["UtilitiesBaseMap", "WaterBroadcast", "SewerBroadcast", "SewerLayers", "StormBroadcast", "StormLayers", "StormwaterBMPs", "SurfaceFlow", "PublicWorks", "Utilities/RasterUtilities", "Utilities/Symbols"],
        "LAW_ENFORCEMENT_PUBLIC_SAFETY": ["WebPolice", "WebFire", "CityFacilities", "WebCityServices"],
        "GEOCODING_ADDRESSING_REGISTRY": ["AddressLocator", "CompositeLocator", "AddressEdits", "WebAddresses", "Test/CompositePro83", "Basemap", "BusinessAnalysis", "Business"]
    }

    categorized_layers = []
    for item in gis_catalog:
        name = item["name"]
        matched_cat = "UNCATEGORIZED_MUNICIPAL"
        for cat, layers in categories.items():
            if name in layers:
                matched_cat = cat
                break
        
        base_url = item["url"]
        query_url = f"{base_url}/0/query?where=1=1&outFields=*&f=json" if item["type"] in ["MapServer", "FeatureServer"] else base_url
        lightbox_url = f"{base_url}/export?bbox=-13145000,3985000,-13130000,3995000&size=1200,900&f=image" if ("Aerial" in name or "Ortho" in name) else None

        layer_entry = {
            "service_name": name,
            "type": item["type"],
            "category": matched_cat,
            "url": base_url,
            "rest_query_url": query_url,
            "lightbox_sample_url": lightbox_url,
            "layers_count": item.get("layers_count", 0),
            "tables_count": item.get("tables_count", 0),
            "description": item.get("description", ""),
            "status": item.get("status", "ONLINE_ACCESSIBLE")
        }
        categorized_layers.append(layer_entry)

    neo_gis_matrix = {
        "agent_codename": "NEO",
        "subsystem": "MUNICIPAL_GIS_TACTICAL_RADAR",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_endpoints": len(categorized_layers),
        "breakdown_by_category": {cat: len([x for x in categorized_layers if x["category"] == cat]) for cat in categories.keys()},
        "services": categorized_layers
    }

    out_file = PROJECT_ROOT / "data" / "neo_internal_hb_gis_intelligence.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(neo_gis_matrix, f, indent=2)

    print(f"SUCCESS: Compiled Neo GIS Intelligence Matrix -> {out_file} ({len(categorized_layers)} endpoints)")

if __name__ == "__main__":
    build_neo_gis_engine()
