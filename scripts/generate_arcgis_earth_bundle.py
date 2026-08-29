#!/usr/bin/env python3
"""
scripts/generate_arcgis_earth_bundle.py
======================================
Generates full 3D geospatial intelligence layers (KML, KMZ, GeoJSON) for ArcGIS Earth
and Google Earth covering all 4 core court matters, municipal parcels, SLA boundaries,
and aerial corridors in OsintNeoAi.
"""

import os
import json
import zipfile

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "opencode_work")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# Feature Definitions
# ------------------------------------------------------------------------------

PLACEMARKS = [
    {
        "name": "Angel Stadium 153-Acre Surplus Land Zone (USA v. Sidhu)",
        "lat": 33.8003,
        "lon": -117.8827,
        "alt": 48,
        "category": "Surplus Land Act / Wire Fraud",
        "description": "Site of $320,000,000.00 land transaction voided unanimously under Anaheim City Resolution 2022-064 following FBI SA Brian Adkins wiretap intercepts and California HCD $96M SLA violation notice (Docket 8:23-cr-00108-CJC)."
    },
    {
        "name": "Anaheim City Hall & Chamber of Commerce (USA v. Ament)",
        "lat": 33.8353,
        "lon": -117.9145,
        "alt": 45,
        "category": "Municipal Bribery & Slush Fund Hub",
        "description": "Anaheim Chamber of Commerce operational hub and $225k slush wire fraud nexus (Docket 8:22-cr-00078-CJC)."
    },
    {
        "name": "USDC Central District of California - Santa Ana Courthouse",
        "lat": 33.7486,
        "lon": -117.8705,
        "alt": 40,
        "category": "Federal Judicial District",
        "description": "Ronald Reagan Federal Building. Courtroom of Hon. Cormac J. Carney presiding over federal criminal matters 8:23-cr-00108-CJC and 8:22-cr-00078-CJC."
    },
    {
        "name": "Orange County Superior Court - Central Justice Center (CJC)",
        "lat": 33.7533,
        "lon": -117.8741,
        "alt": 42,
        "category": "State Judicial Center",
        "description": "700 W Civic Center Dr, Santa Ana. Venue of Woodbridge Meadows v. Dimarcello (Docket 30-2021-01201327-CL-UD-CJC) featuring triple void defaults entered after 4:29 PM statutory stay under Cal. CCP § 170.6."
    },
    {
        "name": "11770 Warner Ave Commercial Asset Hub",
        "lat": 33.7161,
        "lon": -117.9275,
        "alt": 25,
        "category": "Commercial Real Estate Asset",
        "description": "Commercial parcel nexus connecting Fountain Valley and Garden Grove municipal asset corridors."
    },
    {
        "name": "Corona Municipal Airport (KAJO) - Dogs Day Helicopter Hangar",
        "lat": 33.8978,
        "lon": -117.6322,
        "alt": 162,
        "category": "Aviation Asset Hub",
        "description": "Base of Dogs Day Productions helicopter assets ($158,875.00 value / $15,887.50 sales tax evasion audit)."
    },
    {
        "name": "John Wayne Airport (KSNA)",
        "lat": 33.6762,
        "lon": -117.8675,
        "alt": 17,
        "category": "Aviation Transit Hub",
        "description": "Origin of commercial and charter flight segments linked to Orange County municipal leadership."
    },
    {
        "name": "Hamilton Township Police Department & Municipal Complex (NJ)",
        "lat": 40.2315,
        "lon": -74.7088,
        "alt": 30,
        "category": "Law Enforcement Nexus",
        "description": "Incident Report 2019-00053723 & ShopRite commercial nexus."
    },
    {
        "name": "Ewing Township Police Department (NJ)",
        "lat": 40.2643,
        "lon": -74.7985,
        "alt": 45,
        "category": "Law Enforcement Nexus",
        "description": "Ewing Police Department tactical jurisdiction and FBI SA Bradley H. Zartman coordination."
    },
    {
        "name": "USDC District of New Jersey - Trenton Federal Courthouse",
        "lat": 40.2206,
        "lon": -74.7645,
        "alt": 18,
        "category": "Federal Judicial District",
        "description": "Clarkson S. Fisher Federal Building & U.S. Courthouse. Venue of USA v. Christopher Ryan (Docket 3:20-mj-05007-TJB)."
    }
]

PARCELS = [
    {
        "name": "Angel Stadium 153-Acre Parcel Perimeter",
        "description": "Boundary polygon of the 153-acre Angel Stadium property subjected to California Surplus Land Act (SLA) $96,000,000.00 statutory penalty.",
        "coordinates": [
            [-117.8860, 33.8050, 50],
            [-117.8780, 33.8045, 50],
            [-117.8775, 33.7960, 50],
            [-117.8865, 33.7965, 50],
            [-117.8860, 33.8050, 50]
        ]
    }
]

FLIGHT_PATHS = [
    {
        "name": "Helicopter Flight Corridor: KSNA to KAJO",
        "description": "Aviation flight vector between John Wayne Airport and Corona Municipal Airport.",
        "coordinates": [
            [-117.8675, 33.6762, 500],
            [-117.7800, 33.7600, 1200],
            [-117.7000, 33.8400, 1500],
            [-117.6322, 33.8978, 200]
        ]
    },
    {
        "name": "Mercer County Law Enforcement Corridor (Hamilton -> Ewing -> Trenton)",
        "description": "Tactical law enforcement operational vector connecting Hamilton PD, Ewing PD, and Trenton Federal Courthouse.",
        "coordinates": [
            [-74.7088, 40.2315, 50],
            [-74.7500, 40.2500, 100],
            [-74.7985, 40.2643, 80],
            [-74.7645, 40.2206, 30]
        ]
    }
]

# ------------------------------------------------------------------------------
# KML Generation
# ------------------------------------------------------------------------------

def generate_kml():
    kml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '  <Document>',
        '    <name>OsintNeoAi Master Forensic Intelligence Layers</name>',
        '    <open>1</open>',
        '    <description>Court-verified geospatial layers, 3D boundaries, and flight vectors for OsintNeoAi.</description>',
        '    <Style id="redPin">',
        '      <IconStyle><color>ff0000ff</color><scale>1.2</scale></IconStyle>',
        '      <LabelStyle><scale>0.9</scale></LabelStyle>',
        '    </Style>',
        '    <Style id="cyanPin">',
        '      <IconStyle><color>ffffff00</color><scale>1.2</scale></IconStyle>',
        '      <LabelStyle><scale>0.9</scale></LabelStyle>',
        '    </Style>',
        '    <Style id="polygonStyle">',
        '      <LineStyle><color>ff00e5ff</color><width>3</width></LineStyle>',
        '      <PolyStyle><color>4d00e5ff</color></PolyStyle>',
        '    </Style>',
        '    <Style id="flightPathStyle">',
        '      <LineStyle><color>ffffaa00</color><width>4</width></LineStyle>',
        '    </Style>',
        '    <Folder>',
        '      <name>📍 Key Investigation Placemarks</name>'
    ]

    for p in PLACEMARKS:
        kml.extend([
            '      <Placemark>',
            f'        <name>{p["name"]}</name>',
            '        <styleUrl>#cyanPin</styleUrl>',
            f'        <description><![CDATA[<h3>{p["name"]}</h3><p><b>Category:</b> {p["category"]}</p><p>{p["description"]}</p>]]></description>',
            '        <Point>',
            '          <altitudeMode>relativeToGround</altitudeMode>',
            f'          <coordinates>{p["lon"]},{p["lat"]},{p["alt"]}</coordinates>',
            '        </Point>',
            '      </Placemark>'
        ])

    kml.extend([
        '    </Folder>',
        '    <Folder>',
        '      <name>🔷 Municipal Parcels & SLA Boundaries</name>'
    ])

    for poly in PARCELS:
        coord_str = " ".join([f"{c[0]},{c[1]},{c[2]}" for c in poly["coordinates"]])
        kml.extend([
            '      <Placemark>',
            f'        <name>{poly["name"]}</name>',
            '        <styleUrl>#polygonStyle</styleUrl>',
            f'        <description><![CDATA[<h3>{poly["name"]}</h3><p>{poly["description"]}</p>]]></description>',
            '        <Polygon>',
            '          <extrude>1</extrude>',
            '          <altitudeMode>relativeToGround</altitudeMode>',
            '          <outerBoundaryIs>',
            '            <LinearRing>',
            f'              <coordinates>{coord_str}</coordinates>',
            '            </LinearRing>',
            '          </outerBoundaryIs>',
            '        </Polygon>',
            '      </Placemark>'
        ])

    kml.extend([
        '    </Folder>',
        '    <Folder>',
        '      <name>✈️ 3D Flight & Enforcement Corridors</name>'
    ])

    for path in FLIGHT_PATHS:
        coord_str = " ".join([f"{c[0]},{c[1]},{c[2]}" for c in path["coordinates"]])
        kml.extend([
            '      <Placemark>',
            f'        <name>{path["name"]}</name>',
            '        <styleUrl>#flightPathStyle</styleUrl>',
            f'        <description><![CDATA[<h3>{path["name"]}</h3><p>{path["description"]}</p>]]></description>',
            '        <LineString>',
            '          <extrude>1</extrude>',
            '          <tessellate>1</tessellate>',
            '          <altitudeMode>relativeToGround</altitudeMode>',
            f'          <coordinates>{coord_str}</coordinates>',
            '        </LineString>',
            '      </Placemark>'
        ])

    kml.extend([
        '    </Folder>',
        '  </Document>',
        '</kml>'
    ])

    return "\n".join(kml)

# ------------------------------------------------------------------------------
# GeoJSON Generation
# ------------------------------------------------------------------------------

def generate_geojson():
    features = []

    for p in PLACEMARKS:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [p["lon"], p["lat"], p["alt"]]
            },
            "properties": {
                "name": p["name"],
                "category": p["category"],
                "description": p["description"]
            }
        })

    for poly in PARCELS:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[c[0], c[1]] for c in poly["coordinates"]]]
            },
            "properties": {
                "name": poly["name"],
                "description": poly["description"]
            }
        })

    for path in FLIGHT_PATHS:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[c[0], c[1], c[2]] for c in path["coordinates"]]
            },
            "properties": {
                "name": path["name"],
                "description": path["description"]
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }

# ------------------------------------------------------------------------------
# Execution & Packaging
# ------------------------------------------------------------------------------

def main():
    kml_content = generate_kml()
    kml_path = os.path.join(OUTPUT_DIR, "OsintNeoAi_Master_Investigation.kml")
    with open(kml_path, "w", encoding="utf-8") as f:
        f.write(kml_content)
    print(f"✓ Created KML file: {kml_path}")

    kmz_path = os.path.join(OUTPUT_DIR, "OsintNeoAi_Master_Investigation.kmz")
    with zipfile.ZipFile(kmz_path, "w", zipfile.ZIP_DEFLATED) as kmz:
        kmz.write(kml_path, "doc.kml")
    print(f"✓ Created KMZ bundle: {kmz_path}")

    geojson_data = generate_geojson()
    geojson_path = os.path.join(OUTPUT_DIR, "OsintNeoAi_Master_Investigation.geojson")
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)
    print(f"✓ Created GeoJSON layer: {geojson_path}")

if __name__ == "__main__":
    main()
