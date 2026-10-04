"""
arcgis_for_teams_exporter.py — OSINT Neo AI ArcGIS for Teams Spatial Exporter
Extracts spatial intelligence nodes (Toxic Sites, LLC Shells, Plume Vectors, Sinkholes, Infrastructure)
and converts them into Esri FeatureCollection JSON and GeoJSON format for ArcGIS for Teams.
"""

import json
import os

# Spatial Intelligence Nodes Dataset
SPATIAL_FEATURES = [
    {
        "id": "TOX-001",
        "name": "HBNC Toxic Site",
        "type": "Toxic Site",
        "category": "Toxic",
        "latitude": 33.6775,
        "longitude": -118.0012,
        "address": "17642 Beach Blvd / 17631 Cameron Ln, Huntington Beach, CA",
        "apn": "102-451-09",
        "severity": "CRITICAL",
        "description": "Cr-VI 980 µg/kg (49x RSL). Asphalt cap failing. 2,247 cu ft HDPE Stormtech chambers. Void ab initio clearance. $155M COC liability.",
        "case_ref": "8:26-cv-00348"
    },
    {
        "id": "TOX-002",
        "name": "Cameron Ln Parcel",
        "type": "Toxic Site",
        "category": "Toxic",
        "latitude": 33.6770,
        "longitude": -118.0015,
        "address": "17631 Cameron Ln, Huntington Beach, CA",
        "apn": "102-451-10",
        "severity": "HIGH",
        "description": "Asbestos/Lead paint. Former agricultural pesticides. Yamada Trustee 1998 acquisition.",
        "case_ref": "8:26-cv-00348"
    },
    {
        "id": "TOX-003",
        "name": "Center Ave Vaults",
        "type": "Underground Vault",
        "category": "Toxic",
        "latitude": 33.6927,
        "longitude": -117.9974,
        "address": "7561 Center Ave, Units D1-E1-G3-J1, Huntington Beach, CA",
        "apn": "107-120-14",
        "severity": "CRITICAL",
        "description": "Underground concrete vaults (1960s-70s). 4 shell LLCs. Chen-Yamada pipeline routing $1.47M PPP.",
        "case_ref": "8:26-cv-00348"
    },
    {
        "id": "LLC-001",
        "name": "Stewart Industrial Entity",
        "type": "Shell LLC",
        "category": "LLC Shell",
        "latitude": 33.7530,
        "longitude": -118.0720,
        "address": "10832 Stewart St, Westminster, CA",
        "apn": "097-220-04",
        "severity": "MEDIUM",
        "description": "Primary registration hub for regional LLCs. Routing hub to PCH CMRA.",
        "case_ref": "8:26-cv-00348"
    },
    {
        "id": "LLC-002",
        "name": "Newport Shell Cluster",
        "type": "Shell LLC",
        "category": "LLC Shell",
        "latitude": 33.6500,
        "longitude": -117.8950,
        "address": "20341 Irvine Ave, Newport Beach, CA",
        "apn": "439-011-02",
        "severity": "HIGH",
        "description": "CSJ Management / PL Jetty $0 transfers hub.",
        "case_ref": "8:26-cv-00348"
    },
    {
        "id": "LLC-003",
        "name": "Pham Quitclaim Nexus",
        "type": "Quitclaim Target",
        "category": "LLC Shell",
        "latitude": 33.7450,
        "longitude": -117.8125,
        "address": "2614 Orchard Dr, Santa Ana, CA",
        "apn": "011-340-19",
        "severity": "HIGH",
        "description": "Quitclaim deed transfer hub ($0 consideration). Pham Family Trust.",
        "case_ref": "8:26-cv-00348"
    },
    {
        "id": "INF-001",
        "name": "Huntington Beach Police Dept",
        "type": "Municipal Node",
        "category": "Infrastructure",
        "latitude": 33.6603,
        "longitude": -117.9992,
        "address": "2000 Main St, Huntington Beach, CA",
        "apn": "158-091-01",
        "severity": "INFO",
        "description": "Municipal Police HQ. Network port audit target site.",
        "case_ref": "8:26-cv-00348"
    },
    {
        "id": "INF-002",
        "name": "Huntington Beach City Hall",
        "type": "Municipal Node",
        "category": "Infrastructure",
        "latitude": 33.6598,
        "longitude": -117.9985,
        "address": "2000 Main St, Huntington Beach, CA",
        "apn": "158-091-02",
        "severity": "INFO",
        "description": "Huntington Beach City Hall & CEQA record repository.",
        "case_ref": "8:26-cv-00348"
    }
]

def generate_geojson(features, output_path):
    """Generates standard GeoJSON FeatureCollection for ArcGIS Online / Teams."""
    geojson_features = []
    for f in features:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [f["longitude"], f["latitude"]]
            },
            "properties": {
                "ID": f["id"],
                "Name": f["name"],
                "Type": f["type"],
                "Category": f["category"],
                "Address": f["address"],
                "APN": f["apn"],
                "Severity": f["severity"],
                "Description": f["description"],
                "Case_Ref": f["case_ref"]
            }
        }
        geojson_features.append(feature)
        
    geojson_data = {
        "type": "FeatureCollection",
        "name": "OSINT_Neo_AI_ArcGIS_Teams_Spatial_Intel",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": geojson_features
    }
    
    with open(output_path, "w", encoding="utf-8") as out_f:
        json.dump(geojson_data, out_f, indent=2)
    print(f"[+] Successfully exported GeoJSON: {output_path} ({len(features)} features)")
    return geojson_data

def generate_esri_feature_collection(features, output_path):
    """Generates Esri FeatureCollection JSON compatible with ArcGIS Web Map spec."""
    esri_features = []
    for idx, f in enumerate(features, 1):
        esri_f = {
            "attributes": {
                "FID": idx,
                "ID": f["id"],
                "Name": f["name"],
                "Type": f["type"],
                "Category": f["category"],
                "Address": f["address"],
                "APN": f["apn"],
                "Severity": f["severity"],
                "Description": f["description"],
                "Case_Ref": f["case_ref"]
            },
            "geometry": {
                "x": f["longitude"],
                "y": f["latitude"],
                "spatialReference": {"wkid": 4326}
            }
        }
        esri_features.append(esri_f)

    feature_layer = {
        "layerDefinition": {
            "name": "OSINT Neo AI Spatial Targets",
            "type": "Feature Layer",
            "geometryType": "esriGeometryPoint",
            "spatialReference": {"wkid": 4326},
            "fields": [
                {"name": "FID", "type": "esriFieldTypeOID", "alias": "FID"},
                {"name": "ID", "type": "esriFieldTypeString", "alias": "Target ID"},
                {"name": "Name", "type": "esriFieldTypeString", "alias": "Name"},
                {"name": "Type", "type": "esriFieldTypeString", "alias": "Type"},
                {"name": "Category", "type": "esriFieldTypeString", "alias": "Category"},
                {"name": "Address", "type": "esriFieldTypeString", "alias": "Address"},
                {"name": "APN", "type": "esriFieldTypeString", "alias": "APN"},
                {"name": "Severity", "type": "esriFieldTypeString", "alias": "Severity"},
                {"name": "Description", "type": "esriFieldTypeString", "alias": "Description"},
                {"name": "Case_Ref", "type": "esriFieldTypeString", "alias": "Case Reference"}
            ]
        },
        "featureSet": {
            "features": esri_features,
            "geometryType": "esriGeometryPoint"
        }
    }

    with open(output_path, "w", encoding="utf-8") as out_f:
        json.dump(feature_layer, out_f, indent=2)
    print(f"[+] Successfully exported Esri Feature Collection: {output_path}")
    return feature_layer

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    geojson_out = os.path.join(base_dir, "arcgis_for_teams_geojson.geojson")
    esri_out = os.path.join(base_dir, "arcgis_for_teams_feature_collection.json")
    
    generate_geojson(SPATIAL_FEATURES, geojson_out)
    generate_esri_feature_collection(SPATIAL_FEATURES, esri_out)
