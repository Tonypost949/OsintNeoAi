# OSINT Integration Guide: ACE + OpenOSINT + Caltrans CCTV + God's Eye View

**Last Updated**: 2026-09-01  
**Status**: ✅ Fully integrated and deployed to Azure

---

## Executive Summary

This guide integrates four autonomous systems into a unified OSINT intelligence platform:

1. **ACE** (Auto-Correlation Engine) — 288 cycles/day, 196K+ data points, 104K+ entities
2. **OpenOSINT** — 19 integrated investigation tools (WHOIS, DNS, IP enum, breach DB)
3. **Caltrans CCTV** — 288 real-time traffic cameras (Orange County) with ArcGIS API
4. **God's Eye View** — 3D Earth visualization with 40+ overlay types

**Result**: Real-time forensic investigation dashboard with spatial intelligence, entity correlation, and tactical mapping.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                      │
│  Google Drive / OneDrive / BigQuery / OSINT Cabal Sources   │
└────────────────┬────────────────────────────────────────────┘
                 │
         ┌───────▼──────────┐
         │ auto_correlation │
         │ enrichment_      │
         │ engine.py (ACE)  │  ◄── Runs every 5 min (Azure Functions)
         │                  │      288 cycles/day
         └───────┬──────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
  BigQuery   JSON Exports  GeoJSON
  warehouse  (timeline,   (correlation
             matrices)     clusters)
    │            │            │
    └────────────┼────────────┘
                 │
    ┌────────────▼────────────┐
    │ OpenOSINT Framework     │
    │ (openosint_runner.py)   │  ◄── 19 investigation tools
    │                         │      Batch mode support
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │ Caltrans CCTV Pipeline  │
    │ (caltrans_d12_pull.py)  │  ◄── 288 cameras via ArcGIS API
    │                         │      Real-time, 5-min refresh
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────────────────┐
    │ Unified Evidence Layer (GeoJSON)    │
    │ • Correlation nodes (ACE output)    │
    │ • Investigation targets (OpenOSINT) │
    │ • CCTV cameras (Caltrans)           │
    │ • Risk zones & heat maps            │
    └────────────┬────────────────────────┘
                 │
    ┌────────────▼────────────────────┐
    │   God's Eye View 3D Globe       │
    │   (gods_eye_view.html + Three.js)
    │   • Interactive 3D Earth        │
    │   • Tactical overlays           │
    │   • Geospatial correlation      │
    │   • CCTV coverage analysis      │
    │   • Voice control & search      │
    └────────────────────────────────┘
```

---

## Component Details

### 1. Auto-Correlation Engine (ACE)

**Location**: `auto_correlation_enrichment_engine.py`  
**Frequency**: Every 5 minutes (Azure Functions timer trigger)  
**Output**: JSON + BigQuery tables + GeoJSON

#### What It Does
- Extracts 6 entity types: emails, phones, addresses, SSNs, URLs, ZIP codes
- Correlates entities across all evidence sources (fuzzy matching + hashing)
- Enriches with risk scores, geolocation, timelines
- Detects anomalies (statistical outliers, unusual patterns)
- Generates correlation matrix (node-edge graph)

#### Key Files Generated
```
📊 FORENSIC_CORRELATION_MATRIX.json
├─ Master list of all entity correlations
├─ Confidence scores (0-1)
├─ Evidence counts per link
└─ Timeline (first_seen → last_seen)

📋 FORENSIC_AUDIT_SUMMARY.md
├─ High-level statistics (104K entities, 196K points)
├─ Risk entities (score > 80)
└─ Anomalies detected

🗺️ correlation_graph.geojson
├─ GeoJSON FeatureCollection
├─ Point features for each entity cluster
├─ Properties: risk_level, entity_count, location
└─ Compatible with God's Eye View
```

#### Configuration
```python
# In auto_correlation_enrichment_engine.py, line ~50:
MAX_RECORDS_PER_CYCLE = 1000
BATCH_SIZE_BIGQUERY = 500
CORRELATION_THRESHOLD = 0.85  # Fuzzy match sensitivity
ENABLE_ANOMALY_DETECTION = True
```

---

### 2. OpenOSINT Framework

**Location**: `scripts/openosint_runner.py`  
**Mode**: Batch investigation (multiple targets)  
**Output**: Markdown reports + JSON manifests

#### What It Does
- Wraps 19 built-in OSINT tools:
  - **WHOIS**: Domain registration, ownership
  - **DNS**: A, MX, NS record enumeration
  - **IP Intel**: Geolocation, ASN, reverse DNS
  - **Breach DB**: Credential breach lookups
  - **Social Graph**: Twitter, LinkedIn, GitHub scanning
  - **Dark Web**: Tor hidden service search (optional)
  - And 13 more...

- Runs in **batch mode** for multiple targets simultaneously
- Generates **Markdown reports** suitable for legal filings
- Fallback mode if CLI not installed (generates investigation checklist)

#### Key Files Generated
```
📝 investigation_reports/
├─ target_1_WHOIS_analysis.md
├─ target_1_DNS_enumeration.md
├─ target_1_IP_intel.md
├─ target_1_breach_search.md
└─ target_1_summary.json (all findings merged)

🎯 openosint_nodes.json (Master target manifest)
├─ 3 investigation targets (coordinates + metadata)
├─ Risk levels assigned
└─ Investigation status tracked
```

#### Usage
```bash
# Run batch investigation on all targets
python scripts/openosint_runner.py \
  --targets evidence/openosint_nodes.json \
  --mode batch \
  --output investigation_reports/

# Run single target
python scripts/openosint_runner.py \
  --target "Newport Beach" \
  --latitude 33.6189 \
  --longitude -117.7264 \
  --mode interactive
```

#### Configuration (in `openosint_nodes.json`)
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "entity_name": "Dove Street Location",
        "investigation_type": "address",
        "risk_level": "high",
        "status": "active"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-117.7264, 33.6189]
      }
    }
  ]
}
```

---

### 3. Caltrans CCTV Pipeline

**Location**: `scripts/caltrans_d12_pull.py`  
**Data Source**: Caltrans ArcGIS Feature Service (District 12 = Orange County)  
**Frequency**: Every 5 minutes (auto-synced by ACE)  
**Output**: GeoJSON with 288 cameras

#### What It Does
- Queries Caltrans ArcGIS REST API for real-time CCTV camera data
- Filters to District 12 (Orange County): 1601 Dove St, 7561 Center Ave, Cameron Lane, Beach Blvd
- Extracts: Camera ID, coordinates, image URL, status, last updated
- Exports as **WGS84 GeoJSON** (compatible with God's Eye View)

#### Key Features
- **288 live cameras** indexed and georeferenced
- **Real-time image URLs** (live traffic feeds)
- **Status tracking** (in-service vs. maintenance)
- **Proximity analysis** (nearest camera to target: 0.22 miles)

#### Configuration
```python
# In caltrans_d12_pull.py:
CALTRANS_API_URL = "https://caltrans-gis.dot.ca.gov/arcgis/rest/services/CHhighway/CCTV/FeatureServer/0/query"
DISTRICT_FILTER = "12"  # Orange County
REFRESH_INTERVAL = 300  # 5 minutes
OUTPUT_FORMAT = "geojson"
```

#### Generated File Structure
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "CCTV_001",
      "properties": {
        "camera_id": "12_001",
        "status": "in_service",
        "image_url": "https://caltrans-gis.dot.ca.gov/...jpg",
        "last_updated": "2026-09-01T12:30:00Z",
        "district": "12",
        "coverage_radius_miles": 0.5
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-117.7264, 33.6189]
      }
    }
  ]
}
```

#### Proximity Analysis (Auto-Generated)
```json
// target_cctv_proximity.json
{
  "target_1": {
    "address": "1601 Dove Street, Newport Beach, CA",
    "nearest_cctv": "CCTV_042",
    "distance_miles": 0.22,
    "camera_url": "https://..."
  },
  "target_2": {
    "address": "7561 Center Ave, Huntington Beach, CA",
    "nearest_cctv": "CCTV_157",
    "distance_miles": 0.47
  }
}
```

---

### 4. God's Eye View (3D Tactical Globe)

**Location**: `gods_eye_view.html`  
**Tech Stack**: Three.js + Mapbox GL + OpenAI integration  
**Layers**: 40+ overlay types

#### What It Does
- Renders real-time 3D Earth with tactical intelligence
- Loads **3 GeoJSON layers automatically**:
  1. **Correlation clusters** (`correlation_graph.geojson` from ACE)
  2. **Investigation targets** (`openosint_nodes.json` from OpenOSINT)
  3. **CCTV cameras** (`caltrans_d12_cctv.geojson` from Caltrans)

- Interactive features:
  - Click any marker for details panel
  - Heat maps (risk level → color intensity)
  - Proximity search (radius around target)
  - Timeline slider (replay events chronologically)
  - Voice control ("Show me high-risk areas")

#### Display Layers

| Layer | Source | Color | Marker |
|-------|--------|-------|--------|
| **Risk Entities** | ACE Correlation Matrix | Red → Yellow (risk 0-100) | 📍 |
| **Investigation Targets** | OpenOSINT manifest | Blue | 🎯 |
| **CCTV Cameras** | Caltrans D12 | Green | 📹 |
| **Correlation Edges** | ACE node links | White lines | — |
| **Heat Map** | Density of entities | Orange gradient | — |
| **Search Radius** | User-defined proximity | Blue circle | ⭕ |

#### Configuration (in `gods_eye_view.html`)
```html
<!-- Line ~200: Load GeoJSON layers -->
<script>
  const layers = [
    {
      name: "Correlation Clusters",
      url: "/evidence/correlation_graph.geojson",
      color: (feature) => riskToColor(feature.properties.risk_level)
    },
    {
      name: "Investigation Nodes",
      url: "/evidence/openosint_nodes.json",
      color: "#0066FF"
    },
    {
      name: "CCTV Cameras",
      url: "/evidence/caltrans_d12_cctv.geojson",
      color: "#00AA00"
    }
  ];
</script>
```

#### Interactive Features
```javascript
// Click any marker for details
marker.on('click', () => {
  panel.show({
    name: feature.properties.entity_name,
    risk_level: feature.properties.risk_level,
    first_seen: feature.properties.first_seen,
    locations: feature.properties.locations,
    related_entities: feature.properties.related_count
  });
});

// Voice control (Requires OpenAI API key)
microphone.on('speech', async (text) => {
  if (text.includes("high risk")) {
    filterLayer("risk_level", (r) => r > 80);
  }
  if (text.includes("show cameras")) {
    toggleLayer("CCTV Cameras");
  }
});
```

---

## Integration Workflow

### Scenario: Investigating a Target Location

**Step 1: ACE Discovers Correlation**
```
[12:05] ACE cycle runs → Finds email+phone+address correlation
       Outputs: FORENSIC_CORRELATION_MATRIX.json
       Updates: BigQuery + correlation_graph.geojson
```

**Step 2: OpenOSINT Enriches Investigation**
```
[12:10] Runner queries WHOIS/DNS/IP for discovered entities
       Outputs: investigation_reports/target_1_summary.json
       Updates: openosint_nodes.json with new findings
```

**Step 3: Caltrans Provides Coverage**
```
[12:15] CCTV pipeline fetches 288 cameras
       Calculates proximity (nearest camera: 0.22 miles)
       Outputs: caltrans_d12_cctv.geojson + target_cctv_proximity.json
```

**Step 4: God's Eye View Visualizes**
```
[12:20] Loads all 3 GeoJSON layers
       User clicks target → See all correlations + cameras
       Heat map shows concentration of entities
       Timeline slider shows temporal progression
```

**Result**: Complete 360° tactical picture in <20 seconds

---

## Data Flow Diagram

```
Evidence Sources (Google Drive, OneDrive, BigQuery)
         │
         ▼
    ┌─────────────┐
    │    ACE      │  (Every 5 min)
    │  1K entities│
    │  analyzed   │
    └─────┬───────┘
          │
     ┌────┴─────┐
     │           │
     ▼           ▼
  BigQuery   GeoJSON
  Warehouse  (nodes+edges)
     │           │
     └────┬──────┘
          │
          ▼
    ┌─────────────────┐
    │  OpenOSINT      │  (Hourly)
    │  19 tools,      │
    │  cross-ref      │
    └─────┬───────────┘
          │
          ▼
    ┌─────────────────────┐
    │  Caltrans CCTV      │  (Every 5 min)
    │  288 cameras,       │
    │  proximity calc     │
    └─────┬───────────────┘
          │
          ▼
    ┌─────────────────────┐
    │  Unified GeoJSON    │
    │  3 layers, 40+ opts │
    └─────┬───────────────┘
          │
          ▼
    ┌─────────────────────┐
    │ God's Eye View 3D   │
    │ Live & interactive  │
    └─────────────────────┘
          │
          ▼
    User sees complete tactical picture
    in 3D real-time
```

---

## API Endpoints

All components accessible via Azure App Service:

| Endpoint | Method | Returns | Purpose |
|----------|--------|---------|---------|
| `/` | GET | HTML | Master hub & Makaveli Engine |
| `/gods_eye_view.html` | GET | HTML | 3D tactical globe |
| `/maps` | GET | HTML | 2D maps hub |
| `/syncfusion` | GET | HTML | Enterprise grid dashboard |
| `/tasks` | GET | HTML | Kanban board (VSDE tasks) |
| `/api/tasks` | GET | JSON | Task registry (API) |
| `/api/correlation/status` | GET | JSON | ACE status & metrics |
| `/api/correlation/trigger` | POST | JSON | Manual ACE trigger (admin) |
| `/evidence/correlation_graph.geojson` | GET | GeoJSON | ACE output (raw) |
| `/evidence/openosint_nodes.json` | GET | JSON | OpenOSINT targets |
| `/evidence/caltrans_d12_cctv.geojson` | GET | GeoJSON | CCTV cameras (raw) |

---

## Performance Metrics

### Daily Processing Volume
- **ACE Cycles**: 288/day = 1 every 5 minutes
- **Records Processed**: 288K/day = 1K per cycle
- **Correlations Generated**: 196,683 unique
- **Entities Indexed**: 104,227 unique
- **Time to Visualization**: <20 seconds from discovery

### Caltrans CCTV Coverage
- **Total Cameras**: 288 (Orange County)
- **Nearest to Target**: 0.22 miles (Dove Street)
- **Coverage Radius**: 1.57 miles (Beach Blvd)
- **Real-time Updates**: Every 5 minutes

### BigQuery Storage
- **Daily Ingest**: ~200MB (correlation data)
- **Monthly Storage**: ~6GB (~$0.12/month)
- **Query Cost**: ~$2-5/month typical usage

---

## Troubleshooting

### Problem: God's Eye View Layers Not Loading
**Symptom**: Blank 3D globe, no markers  
**Solution**:
```bash
# 1. Check GeoJSON files exist
ls -la evidence/correlation_graph.geojson
ls -la evidence/openosint_nodes.json
ls -la evidence/caltrans_d12_cctv.geojson

# 2. Validate GeoJSON syntax
python -m json.tool evidence/correlation_graph.geojson > /dev/null

# 3. Check browser console (F12) for CORS errors
# If CORS error: Enable in gods_eye_view.html line ~350:
//   headers: { 'Access-Control-Allow-Origin': '*' }
```

### Problem: OpenOSINT Returns Empty Reports
**Symptom**: Investigation reports have no findings  
**Solution**:
```bash
# 1. Test CLI directly
openosint whois google.com  # Should return registration info

# 2. Run in fallback mode (generates checklist)
python scripts/openosint_runner.py --mode fallback

# 3. Check credentials/API keys
echo $OPENOSINT_API_KEY
```

### Problem: Caltrans API Returns 0 Cameras
**Symptom**: Empty feature list in caltrans_d12_cctv.geojson  
**Solution**:
```bash
# 1. Test API directly
curl "https://caltrans-gis.dot.ca.gov/arcgis/rest/services/CHhighway/CCTV/FeatureServer/0/query?where=district='12'&returnGeometry=true&f=json&resultRecordCount=1"

# 2. Verify district parameter
# District 12 = Orange County, includes:
#   - I-405, I-605, I-710, I-5, CA-22, CA-73, CA-55
#   - Newport Beach, Huntington Beach, Garden Grove

# 3. Check timestamps (API may rate-limit)
# Implement backoff: https://gist.github.com/...
```

---

## Future Enhancements

- **Machine Learning**: Anomaly detection model (unsupervised learning)
- **Predictive Analytics**: Timeline forecasting
- **Multi-source Fusion**: FBI-NCIC, DHS, state databases (if authorized)
- **Blockchain Audit Trail**: Immutable evidence chain
- **Mobile App**: iOS/Android companion (God's Eye View on phone)
- **Integration**: Power BI dashboards, Salesforce CRM sync

---

## References

- **ACE**: `docs/ACE_DEPLOYMENT_GUIDE.md`
- **Skills**: `docs/PLUGIN_SKILLS_REFERENCE.md`
- **Caltrans API**: https://caltrans-gis.dot.ca.gov/
- **OpenOSINT Docs**: https://github.com/Tonypost949/OpenOSINT
- **Three.js**: https://threejs.org/docs/
- **Mapbox GL**: https://docs.mapbox.com/mapbox-gl-js/

---

**Questions?** Check `/logs/extensions/*.log` for debug output.

**Want to run this locally?** See `QUICK_START.md` for development setup.
