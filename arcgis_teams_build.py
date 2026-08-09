#!/usr/bin/env python3
"""
arcgis_teams_build.py — OSINT Neo AI ArcGIS for Teams package builder.

Builds from REAL evidence embedded in hbnc_rico_gis.html:
  1. arcgis_for_teams_geojson.geojson    — Hosted feature layer source (points, lines, severity)
  2. arcgis_teams_adaptive_card_sample.json — Example Adaptive Card payload
  3. arcgis_teams_dashboard.html         — Self-contained Leaflet dashboard (Teams Website tab)

Every coordinate in this file is traceable to the HBNC RICO GIS evidence map
(repo root: hbnc_rico_gis.html) as sourced per hbnc-gis-v2/README.md chain of custody.

Usage:
    python arcgis_teams_build.py
Outputs are written next to this script.
"""
import json
import os
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_GEOJSON = os.path.join(HERE, "arcgis_for_teams_geojson.geojson")
OUT_CARD = os.path.join(HERE, "arcgis_teams_adaptive_card_sample.json")
OUT_DASH = os.path.join(HERE, "arcgis_teams_dashboard.html")

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

SEVERITY_ORDER = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "INFO": 4}

# ---------------------------------------------------------------------------
# REAL EVIDENCE — coordinates, labels and descriptions from hbnc_rico_gis.html
# ---------------------------------------------------------------------------

TOXIC = [
    ("TOX-001", "HBNC Toxic Site", 33.6775, -118.0012,
     "17642 Beach Blvd / 17631 Cameron Ln | Cr-VI 980 ug/kg (49x limit) | Asphalt cap FAILING | 2,247 cu ft HDPE Stormtech chambers | Void ab initio clearance | $155M COC liability",
     "CRITICAL", "CERCLA / Phase I ESA T10000018579"),
    ("TOX-002", "Cameron Ln Parcel", 33.6770, -118.0015,
     "17631 Cameron Ln | Asbestos/Lead paint | Former ag pesticides | Yamada Trustee 1998", "HIGH", "Parcel survey"),
    ("TOX-003", "7561 Center Ave Vaults", 33.6927, -117.9974,
     "Units D1-E1-G1-J1 | 4 shell LLCs | Underground concrete coffins | Chen-Yamada pipeline | $1.47M PPP / $1.13M PPP routing",
     "CRITICAL", "Parcel + PPP records"),
]

SINKHOLES = [
    ("SINK-001", "7561 Center Ave Vaults", 33.6930, -117.9975,
     "Underground concrete coffins / Chen-Yamada / 1960s-70s construction", "HIGH", "Site assessment"),
    ("SINK-002", "HBNC Excavation", 33.6778, -118.0015,
     "Asphalt cap failure / Cr-VI soil disturbance / 2,247 cu ft HDPE chambers", "CRITICAL", "Site assessment"),
    ("SINK-003", "El Toro Hangars", 33.6755, -117.7305,
     "Contaminated fill burial / Decommissioned MCAS El Toro / PFAS migration", "MEDIUM", "Base closure"),
    ("SINK-004", "Stormtech Chamber Field", 33.6773, -118.0010,
     "HDPE Stormtech SC-740 / 2,247 cu ft / PVC manifold / corrosive soil", "CRITICAL", "Stormtech spec"),
]

BLACKHOLES = [
    ("BH-001", "Newport Shell Cluster", 33.650, -117.895,
     "20341-71 Irvine Ave | CSJ Mgmt / PL Jetty | $0 transfers", "HIGH", "LLC filings"),
    ("BH-002", "Pham Quitclaim Nexus", 33.745, -117.8125,
     "2614 Orchard Dr / 7100 Cerritos #108 / 13801 Shirley #85 | $0 quitclaims", "HIGH", "Deed records"),
    ("BH-003", "Garnet St Routing", 33.753, -117.9905,
     "15822 Garnet St | CMRA layer | Dylan & Andrew mailbox", "MEDIUM", "Mail routing"),
    ("BH-004", "PCH CMRA", 33.7505, -118.0955,
     "1077 Pacific Coast Hwy #247 | Stewart mailbox | Battle Creek MI", "HIGH", "PPP addresses"),
]

LLC_SHELLS = [
    ("LLC-001", "Triumvirate LLC", 33.7070, -117.9580,
     "21951 Brookhurst St | PPP $1,471,840 | Anchorage AK mailbox", "HIGH", "PPP/SBA"),
    ("LLC-002", "Stewart Industrial", 33.7530, -118.0720,
     "3311 Bounty Cir | PPP $1,128,327 | 1076 PCH #247 CMRA", "HIGH", "PPP/SBA"),
    ("LLC-003", "CP Premier 1", 33.8080, -118.0020,
     "7100 Cerritos Ave #108 | Peter Pham $0 quitclaim", "HIGH", "Deed"),
    ("LLC-004", "CP Premier 2", 33.7740, -117.9870,
     "13801 Shirley St #85 | Peter Pham $0 quitclaim", "HIGH", "Deed"),
    ("LLC-005", "Garnet Drop", 33.7530, -117.9900,
     "15821-15822 Garnet St | Dylan & Andrew mailbox CMRA", "MEDIUM", "Mail routing"),
    ("LLC-006", "Newport LLC Cluster", 33.6500, -117.8900,
     "20341-91 Irvine Ave | CSJ/PL Jetty shell cluster", "MEDIUM", "LLC filings"),
    ("LLC-007", "Pham Residence", 33.7450, -117.8120,
     "2614 Orchard Dr Tustin | Peter Pham nexus", "MEDIUM", "Deed"),
    ("LLC-008", "Stewart PPP", 33.7550, -117.9900,
     "PPP $1,128,327 | Bounty Cir | Battle Creek MI", "MEDIUM", "PPP/SBA"),
    ("LLC-009", "Triumvirate PPP", 33.7250, -117.9700,
     "PPP $1,471,840 | Brookhurst | 3705 Arctic Blvd AK", "MEDIUM", "PPP/SBA"),
    ("LLC-010", "ONNI HB LLC", 33.6870, -117.9880,
     "$97.25M | 17011 Beach Blvd | Phoenix mail", "HIGH", "PPP/SBA"),
    ("LLC-011", "Corte Bella TruAmerica", 33.6830, -117.9940,
     "$85.75M | 9543 Dixie St | Woodland Hills mail", "HIGH", "PPP/SBA"),
    ("LLC-012", "Sendero Riverbend", 33.6830, -117.9940,
     "$70M | 8955 Riverbend Dr | LA mail", "HIGH", "PPP/SBA"),
    ("LLC-013", "SCG Edinger Plaza", 33.6890, -117.9850,
     "$65.5M | 7542 Edinger Ave | SF mail", "HIGH", "PPP/SBA"),
]

INFRA = [
    ("I-405 Freeway Corridor", [[33.650, -118.000], [33.730, -117.990]], "INFO", "Transport"),
    ("Pacific Coast Hwy (PCH)", [[33.650, -118.000], [33.730, -117.980]], "INFO", "Transport"),
    ("Beach Boulevard", [[33.677, -118.001], [33.730, -117.990]], "INFO", "Transport"),
    ("HDPE Stormtech Chambers", [[33.6773, -118.0013], [33.6778, -118.0015]], "CRITICAL", "Concealed infrastructure"),
]

FCA_EVENTS = [
    ("FCA-HIT-001", "USDC CD CA — Knabb v. HB RICO / Qui Tam coordination", 33.7480, -117.8700, "CRITICAL", "Federal docket"),
    ("FCA-HIT-007", "USDC CD CA LA — EPA OIG referral", 34.0500, -118.2500, "CRITICAL", "OIG referral"),
    ("FCA-HIT-012", "DOJ Civil Division — qui tam notice", 38.9070, -77.0370, "HIGH", "DOJ notice"),
    ("FCA-HIT-019", "Qui Tam complaint under seal", 33.7480, -117.8700, "CRITICAL", "Sealed complaint"),
    ("FCA-HIT-024", "Relator disclosure served", 33.6760, -118.0015, "HIGH", "Relator disclosure"),
]

CPS_EVENTS = [
    ("CPS-001", "HBNC Child Deaths", 33.6775, -118.0012,
     "4 confirmed deaths | 279 emergencies | CERCLA toxics exposure", "CRITICAL", "OC HCA 20IC002"),
    ("CPS-002", "OC DA Block", 33.7480, -117.8700, "No action on trafficking referrals", "HIGH", "Referral log"),
    ("CPS-003", "HB City Hall", 33.6760, -118.0015, "CEQA exemption fraud | Blocked reporting", "HIGH", "Ordinance 4289"),
    ("CPS-004", "Anaheim CPS Hub", 33.8350, -117.9100, "Shelter billing cluster | COVID fraud", "HIGH", "Licensing"),
    ("CPS-005", "LA County IV-E", 34.0500, -118.2500, "IV-E billing nexus", "HIGH", "IV-E claims"),
]

PROCURE = [
    ("PROC-001", "OC Sheriff Body Cams", 33.7150, -117.8500, 8_500_000, "Open", "Sheriff", "MEDIUM"),
    ("PROC-002", "County IT Security", 33.7480, -117.8700, 2_500_000, "Open", "IT", "MEDIUM"),
    ("PROC-003", "HB Coastal Infrastructure", 33.6760, -118.0000, 12_000_000, "Under Review", "Public Works", "MEDIUM"),
    ("PROC-004", "Anaheim Housing RFQ", 33.8350, -117.9100, 4_500_000, "Closed", "Housing", "INFO"),
    ("PROC-005", "HBNC 155M Remediation", 33.6775, -118.0012, 155_000_000, "VOID", "OCHCA/DPW", "CRITICAL"),
]

PLUME_ORIGIN = (33.6773, -118.0013)
PLUME_VECTORS = [
    [0.0004, -0.0005], [0.0006, -0.0004], [0.0008, -0.0002], [0.0005, -0.0007],
    [-0.0003, -0.0006], [-0.0005, -0.0004], [-0.0007, -0.0001], [0.0002, -0.0009],
    [0.0009, 0.0001], [0.0010, -0.0002], [-0.0008, -0.0003], [-0.0004, -0.0008],
]


def point_feature(fid, name, lat, lng, desc, layer, severity, source, amount=None, status=None, dept=None):
    props = {
        "TargetID": fid,
        "Name": name,
        "Layer": layer,
        "Severity": severity,
        "SeverityRank": SEVERITY_ORDER.get(severity, 9),
        "Description": desc,
        "Source": source,
        "Latitude": round(lat, 6),
        "Longitude": round(lng, 6),
    }
    if amount:
        props["AmountUSD"] = amount
    if status:
        props["Status"] = status
    if dept:
        props["Dept"] = dept
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [round(lng, 6), round(lat, 6)]},
        "properties": props,
    }


def build_geojson():
    features = []
    for fid, name, lat, lng, desc, sev, src in TOXIC:
        features.append(point_feature(fid, name, lat, lng, desc, "TOXIC", sev, src))
    for row in SINKHOLES:
        fid, name, lat, lng, desc, sev, src = row
        features.append(point_feature(fid, name, lat, lng, desc, "SINKHOLE", sev, src))
    for row in BLACKHOLES:
        fid, name, lat, lng, desc, sev, src = row
        features.append(point_feature(fid, name, lat, lng, desc, "BLACKHOLE", sev, src))
    for row in LLC_SHELLS:
        fid, name, lat, lng, desc, sev, src = row
        features.append(point_feature(fid, name, lat, lng, desc, "LLC", sev, src))
    for fid, name, lat, lng, sev, src in FCA_EVENTS:
        features.append(point_feature(fid, name, lat, lng, "", "FCA", sev, src))
    for fid, name, lat, lng, desc, sev, src in CPS_EVENTS:
        features.append(point_feature(fid, name, lat, lng, desc, "CPS", sev, src))
    for fid, name, lat, lng, amount, status, dept, sev in PROCURE:
        features.append(point_feature(fid, name, lat, lng, f"{dept} {status} ${amount:,}",
                                      "PROCUREMENT", sev, "Procurement portal",
                                      amount=amount, status=status, dept=dept))
    for name, line, sev, src in INFRA:
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [[lng, lat] for lat, lng in line]},
            "properties": {"TargetID": name.upper().replace(" ", "_"),
                           "Name": name, "Layer": "INFRA", "Severity": sev,
                           "SeverityRank": SEVERITY_ORDER[sev], "Description": name, "Source": src},
        })
    oy, ox = PLUME_ORIGIN
    for i, (dy, dx) in enumerate(PLUME_VECTORS, 1):
        pts = [[ox, oy]]
        for step in range(1, 7):
            pts.append([round(ox + dx * step * 0.8, 6), round(oy + dy * step * 0.8, 6)])
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": pts},
            "properties": {"TargetID": f"PLUME-{i:03d}", "Name": f"Cr-VI plume vector {i}",
                           "Layer": "PLUME", "Severity": "HIGH", "SeverityRank": 2,
                           "Description": "Groundwater flow vector (SW) from HBNC per Phase I ESA",
                           "Source": "Phase I ESA"},
        })
    return {
        "type": "FeatureCollection",
        "name": "OSINT Neo AI Spatial Targets",
        "generated_utc": NOW,
        "source_document": "hbnc_rico_gis.html (repo root)",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}},
        "features": features,
    }


def sample_card(geojson):
    pts = [f for f in geojson["features"] if f["geometry"]["type"] == "Point"]
    pts.sort(key=lambda f: f["properties"]["SeverityRank"])
    f = pts[0]
    lon, lat = f["geometry"]["coordinates"]
    p = f["properties"]
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "fallbackText": f"ArcGIS Spatial Alert: {p['Name']}",
        "body": [
            {"type": "TextBlock", "text": "ArcGIS Spatial Alert", "weight": "Bolder",
             "size": "Medium", "color": "Attention"},
            {"type": "TextBlock", "text": p["Name"], "weight": "Bolder", "wrap": True},
            {"type": "FactSet", "facts": [
                {"title": "Target ID:", "value": p["TargetID"]},
                {"title": "Layer:", "value": p["Layer"]},
                {"title": "Severity:", "value": p["Severity"]},
                {"title": "Coordinates:", "value": f"{lat}, {lon}"},
                {"title": "Source:", "value": p["Source"]},
            ]},
            {"type": "TextBlock", "text": p.get("Description", ""), "wrap": True, "size": "Small",
             "isSubtle": True},
        ],
        "actions": [
            {"type": "Action.OpenUrl", "title": "Open in ArcGIS",
             "url": "https://www.arcgis.com/home/webmap/viewer.html"},
        ],
        "context": {"generator": "arcgis_teams_card_generator.py",
                    "generated_utc": NOW,
                    "feature_count": len(geojson["features"])},
    }


def gjson(obj):
    return json.dumps(obj, ensure_ascii=False)


def build_dashboard(geojson):
    severity_colors = {"CRITICAL": "#ff3b3b", "HIGH": "#ff9500", "MEDIUM": "#ffd60a", "INFO": "#4dd2ff"}
    rows = []
    feats = [f for f in geojson["features"] if f["geometry"]["type"] == "Point"]
    feats.sort(key=lambda f: f["properties"]["SeverityRank"])
    for f in feats:
        p = f["properties"]
        rows.append(
            "  {{id:'{}', nm:'{}', layer:'{}', sev:'{}', lat:{}, lng:{}, desc:'{}', src:'{}'}}".format(
                p["TargetID"].replace("'", ""), p["Name"].replace("'", " "),
                p["Layer"], p["Severity"], p["Latitude"], p["Longitude"],
                (p.get("Description") or "").replace("'", " ")[:100],
                (p.get("Source") or "").replace("'", " "))
        )
    js_feats = ",\n".join(rows)
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OSINT Neo AI Spatial Dashboard</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body,#map{width:100%;height:100%;background:#0b0f0b;font-family:Segoe UI,system-ui,sans-serif}
#list{position:fixed;top:0;left:0;bottom:0;width:330px;background:rgba(8,12,8,0.97);border-right:1px solid #223;z-index:1000;overflow-y:auto}
#list h1{padding:14px;font-size:13px;color:#7ef07e;border-bottom:1px solid #223a22;letter-spacing:1px}
#list h1 small{display:block;color:#556;font-weight:400;font-size:10px;margin-top:4px;letter-spacing:0}
.entry{padding:10px 14px;border-bottom:1px solid #162216;cursor:pointer}
.entry:hover{background:#12221a}
.entry .sev{display:inline-block;padding:1px 8px;border-radius:10px;color:#000;font-size:9px;font-weight:800;margin-right:8px}
.entry .nm{color:#dfe;font-size:12px}
.entry .dst{color:#778;font-size:10px;margin-top:3px}
.entry .ly{color:#4a4;font-size:9px;text-transform:uppercase;letter-spacing:1px;margin-top:3px}
#card{position:fixed;bottom:12px;left:12px;width:300px;background:#202a20;border:1px solid #3a553a;border-radius:12px;padding:12px 14px;z-index:1500;box-shadow:0 6px 24px #000c;display:none}
#card h3{color:#ff6b6b;font-size:13px;margin-bottom:6px}
#card .r{font-size:11px;color:#cde;margin:2px 0}
#card .r b{color:#fff;display:inline-block;width:92px}
#card a{display:inline-block;margin-top:8px;color:#6f6;font-size:11px;text-decoration:none}
#legend{position:fixed;right:12px;bottom:12px;background:rgba(8,12,8,.9);border:1px solid #223;border-radius:8px;padding:8px 10px;font-size:10px;color:#9aa;z-index:1000;line-height:1.8}
#legend .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
@media(max-width:700px){#list{width:100%;height:45%}#map{top:45%}}
</style>
</head>
<body>
<div id="map"></div>
<div id="list">
<h1>OSINT NEO AI — SPATIAL TARGETS<small>__META__ features | severity-ranked | ArcGIS for Teams ready</small></h1>
</div>
<div id="legend">
<span><span class="dot" style="background:#ff3b3b"></span>CRITICAL</span>
<span><span class="dot" style="background:#ff9500"></span>HIGH</span>
<span><span class="dot" style="background:#ffd60a"></span>MEDIUM</span>
<span><span class="dot" style="background:#4a2ff"></span>INFO</span>
</div>
<div id="card"></div>
<script>
const ROWS = [
__ROWS__
];
const COLORS = {"CRITICAL":"#ff3b3b","HIGH":"#ff9500","MEDIUM":"#ffd60a","INFO":"#4ad2ff"};
const map = L.map('map',{zoomControl:true}).setView([33.6775,-118.0012],16);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{maxZoom:20}).addTo(map);
const markers = {};
ROWS.forEach(r=>{
  const color = COLORS[r.sev]||'#777';
  const m = L.circleMarker([r.lat,r.lng],{radius:r.sev==='CRITICAL'?11:8,color:'#fff'===color?'#1a1a1a':'#fff',weight:1.2,fillColor:color,fillOpacity:0.9})
    .bindPopup('<b>'+r.name+'</b><br/><span style="color:'+color+'">'+r.sev+'</span> — '+r.layer+'<br/>'+r.dst+'<br/><i>'+r.src+'</i>');
  m.addTo(map);
  markers[r.lat+','+r.lng]=m;
});
const list=document.getElementById('list');
ROWS.forEach(r=>{
  const d=document.createElement('div');d.className='entry';
  d.innerHTML='<span class="sev" style="background:'+(COLORS[r.sev]||'#777')+'">'+r.sev+'</span><span class="nm">'+r.name+'</span><div class="dst">'+r.dst+'</div><div class="ly">'+r.layer+'</div>';
  d.onclick=function(){map.setView([r.lat,r.lng],16);(markers[r.lat+','+r.lng]).openPopup();showCard(r);};
  list.appendChild(d);
});
function showCard(r){
  const c=document.getElementById('card');c.style.display='block';
  c.innerHTML='<h3>SPATIAL ALERT — '+r.sev+'</h3>'+
   '<div class="r"><b>Target:</b>'+r.name+'</div>'+
   '<div class="r"><b>Name:</b>'+r.name+'</div>'+
   '<div class="r"><b>Severity:</b>'+r.sev+'</div>'+
   '<div class="r"><b>Coordinates:</b>'+r.lat+', '+r.lng+'</div>'+
   '<div class="r"><b>Evidence:</b>'+r.src+'</div>'+
   '<a href="https://www.arcgis.com/home/webmap/viewer.html" target="_blank">Open in ArcGIS &rarr;</a>';
}
</script>
</body>
</html>
"""
    meta = f"{len(feats)} point targets | generated {NOW[:10]} UTC | source: hbnc_rico_gis.html"
    html = html.replace("__ROWS__", js_feats).replace("__init__", meta)
    return html


def main():
    print("Building ArcGIS for Teams package from HBNC RICO evidence...")
    geojson = build_geojson()
    with open(OUT_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    print(f"[ok] {os.path.basename(OUT_GEOJSON)} ({len(geojson['features'])} features)")
    card = sample_card(geojson)
    with open(OUT_CARD, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2, ensure_ascii=False)
    print(f"[ok] {os.path.basename(OUT_CARD)}")
    with open(OUT_DASH, "w", encoding="utf-8") as f:
        f.write(build_dashboard(geojson))
    print(f"[ok] {os.path.basename(OUT_DASH)}")
    counts = {}
    for f in geojson["features"]:
        counts[f["properties"]["Layer"]] = counts.get(f["properties"]["Layer"], 0) + 1
    for k, v in counts.items():
        print(f"     {k}: {v}")


if __name__ == "__main__":
    main()