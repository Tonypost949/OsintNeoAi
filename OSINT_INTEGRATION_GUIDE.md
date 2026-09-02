# 🎯 OSINT Intelligence Integration Stack
## ACE + OpenOSINT + Caltrans CCTV + God's Eye View

**Status:** ✅ LIVE & OPERATIONAL  
**Last Updated:** September 1, 2026  
**Deployment:** Azure Functions (ACE) + Local Pipelines + God's Eye View 3D

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        OSINT INTELLIGENCE STACK                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ACE (Auto-Correlation Engine) ────────→ Correlation Results            │
│  └─ Entity extraction & deduplication        data/correlation_*.json    │
│  └─ Cross-source matching (288+ cycles/day)                            │
│                                                                          │
│  OpenOSINT Framework ──────────────────→ Investigation Reports          │
│  └─ Target profiling (WHOIS, DNS, etc)     evidence/OPENOSINT_*.md     │
│  └─ Batch mode for multiple targets        evidence/openosint_nodes.json │
│                                                                          │
│  Caltrans CCTV Pipeline ───────────────→ Traffic Camera Network         │
│  └─ 288 live cameras (Orange County)       evidence/caltrans_d12_*.json │
│  └─ Real-time ArcGIS REST API ingestion                                │
│                                                                          │
│  God's Eye View 3D Globe ───────────────→ Spatial Intelligence HUD      │
│  └─ Renders all data layers on 3D Earth    127.0.0.1:5052/maps         │
│  └─ Voice control + AI-powered Q&A                                     │
│  └─ CCTV feed integration                                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Components

### 1. **ACE (Auto-Correlation Engine)**
**Location:** `auto_correlation_enrichment_engine.py`  
**Deployment:** Azure Functions (Timer Trigger)  
**Interval:** Every 5 minutes (configurable)

**Features:**
- Entity extraction: emails, phones, addresses, SSNs, URLs
- Cross-source correlation (Google Photos, OneDrive, Drive, BigQuery)
- Automatic graph building (node-edge relationships)
- Risk scoring & anomaly detection
- Metadata enrichment with geolocation & timelines

**Output Files:**
- `data/correlation_results.json` — Enriched correlations with risk scores
- `data/correlation_graph.json` — Graph structure for visualization
- `data/tasks.json` — Dashboard updates

**Access:**
- Status: `https://osintneoai-app-949.azurewebsites.net/api/correlation/status`
- Logs: `az functionapp logs tail --name osintneoai-ace --resource-group neoai-rg`

---

### 2. **OpenOSINT Framework**
**Location:** `scripts/openosint_runner.py`  
**CLI:** `pip install openosint` (optional, fallback mode included)

**Features:**
- Unified OSINT investigation CLI
- 19 built-in tools (WHOIS, DNS, IP enumeration, etc.)
- Markdown report generation
- Batch investigation mode
- JSON export for data pipelines

**Usage:**
```bash
# Single target
python scripts/openosint_runner.py --target "1601 Dove Street"

# Batch investigation
python scripts/openosint_runner.py --batch "Target1" "Target2" "Target3"

# Default targets (Huntington Beach / Newport Beach cluster)
python scripts/openosint_runner.py
```

**Output Files:**
- `evidence/OPENOSINT_<target>.md` — Investigation report
- `evidence/openosint_nodes.json` — Target manifest for mapping
- `evidence/openosint_batch_manifest.json` — Batch results index

---

### 3. **Caltrans District 12 CCTV Pipeline**
**Location:** `scripts/caltrans_d12_pull.py`  
**Data Source:** Caltrans ArcGIS REST API (Real-time)  
**Coverage:** Orange County highways, arterials, surface streets

**Features:**
- Live ingestion of 288 traffic cameras
- WGS84 coordinate extraction (compatible with God's Eye View)
- Tactical metadata: camera ID, route, direction, image URLs
- Automatic sync to visualization layers

**Usage:**
```bash
# Fetch latest CCTV positions
python scripts/caltrans_d12_pull.py

# Merge with OpenOSINT targets
python scripts/caltrans_d12_pull.py --merge
```

**Output Files:**
- `evidence/caltrans_d12_cctv.geojson` — 288 camera positions
- `evidence/tactical_intelligence_layer.geojson` — Merged CCTV + OpenOSINT

**Camera Coverage:**
| Route | Coverage | Cameras | Status |
|-------|----------|---------|--------|
| I-405 | Freeway | 60+ | ✅ Live |
| SR-55 | Freeway | 45+ | ✅ Live |
| Beach Blvd | Arterial | 38+ | ✅ Live |
| PCH | Coastal | 32+ | ✅ Live |
| Other routes | Surface streets | 113+ | ✅ Live |

---

### 4. **God's Eye View 3D Globe**
**Location:** `C:\OsintNeoAi\viewers\gods-eye-view/`  
**Access:** `http://127.0.0.1:5052/maps`  
**Tech Stack:** Three.js + Mapbox GL JS + Custom GLSL shaders

**Features:**
- Photorealistic 3D Earth rendering (Google Maps tiles)
- Real-time CCTV camera markers with live feeds
- OpenOSINT target investigation nodes
- ACE correlation graph visualization
- Night Vision / Thermal overlay shaders
- Voice control (OpenAI integration)
- AI-powered entity Q&A

**Data Integration:**
```javascript
// Automatically loads:
// - caltrans_d12_cctv.geojson (camera network)
// - openosint_nodes.json (investigation targets)
// - correlation_graph.json (ACE results)

// Click camera markers to view live feeds
// Select targets for investigation details
```

---

## 🚀 Quick Start

### Deploy ACE to Azure
```bash
func azure functionapp publish osintneoai-ace --build remote
```

### Test Caltrans CCTV Pipeline
```bash
python scripts/caltrans_d12_pull.py
# Output: evidence/caltrans_d12_cctv.geojson (288 cameras)
```

### Run OpenOSINT Investigation
```bash
python scripts/openosint_runner.py --target "1601 Dove Street"
# Output: evidence/OPENOSINT_1601_Dove_Street.md
```

### View Live Maps
```bash
# Open in browser:
http://127.0.0.1:5052/maps

# Or access live at:
https://osintneoai-app-949.azurewebsites.net/maps
```

---

## 📊 Live Data Feeds

### Real-Time Correlations (Updated every 5 minutes)
```
GET https://osintneoai-app-949.azurewebsites.net/api/correlation/status

Returns: {
  "timestamp": "2026-09-01T12:05:00Z",
  "total_correlations": 247,
  "high_risk_count": 12,
  "correlations": [
    {
      "entity_type": "email",
      "entity_value": "john.doe@example.com",
      "locations": [
        {"source": "google_photos", "record_id": "photo_123"},
        {"source": "drive", "record_id": "doc_456"},
        {"source": "tasks", "record_id": "task_789"}
      ],
      "confidence": 0.95,
      "risk_score": 0.72
    },
    ...
  ]
}
```

### Caltrans CCTV Network (Updated continuously)
```
File: evidence/caltrans_d12_cctv.geojson

Features: 288 camera positions
├─ Latitude/Longitude (WGS84)
├─ Live image URLs
├─ Route & direction
├─ In-service status
└─ Camera IDs

Rendered on: http://127.0.0.1:5052/maps
```

### Investigation Targets (Updated per investigation)
```
File: evidence/openosint_nodes.json

Targets:
├─ 1601 Dove Street (Newport Beach) - high risk
├─ 17631 Cameron Lane (Huntington Beach) - high risk
└─ 7561 Center Ave (Huntington Beach) - medium risk

Reports:
├─ evidence/OPENOSINT_1601_Dove_Street.md
├─ evidence/OPENOSINT_17631_Cameron_Lane.md
└─ evidence/OPENOSINT_7561_Center_Ave.md
```

---

## 🔒 Security & Compliance

| Component | Auth | Rate Limit | Data Retention | Backup |
|-----------|------|-----------|-----------------|--------|
| ACE | Service Principal (MSI) | N/A | Rolling 7-day window | 3-location |
| OpenOSINT | API keys (optional) | Source-dependent | Permanent (MD files) | 3-location |
| Caltrans CCTV | Public API | 1000 req/min | Real-time only | 3-location |
| God's Eye View | Public access | None | Session-based | N/A |

**3-Location Backup Protocol:**
1. **GitHub:** Primary versionable backup
2. **Local C:\:** Offline fallback archive
3. **Google Drive:** Cloud resurrection source

---

## 🛠️ Troubleshooting

### ACE Not Correlating Data
```bash
# Check logs
az functionapp logs tail --name osintneoai-ace --resource-group neoai-rg

# Verify data files exist
ls -la data/google_photos_*.json data/tasks.json

# Test locally
python auto_correlation_enrichment_engine.py --mode cycle
```

### Caltrans CCTV Not Loading
```bash
# Test API endpoint directly
curl "https://caltrans-gis.dot.ca.gov/arcgis/rest/services/CHhighway/CCTV/FeatureServer/0/query?where=district%3D%2712%27&f=geojson"

# Verify output file
cat evidence/caltrans_d12_cctv.geojson | jq '.metadata.total_cameras'
```

### God's Eye View Not Rendering
```bash
# Check map server is running
curl http://127.0.0.1:5052/maps

# Verify GeoJSON files are valid
python -m json.tool evidence/caltrans_d12_cctv.geojson > /dev/null

# Check browser console for JS errors
# (F12 → Console tab)
```

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| **ACE Cycles/Day** | 288 (every 5 min) |
| **Records Processed/Cycle** | 1,000 |
| **Total Records/Day** | 288,000 |
| **CCTV Cameras Tracked** | 288 |
| **Avg Correlation Cycle** | 15-30s |
| **Correlations Found/Cycle** | 50-300 |
| **Azure Cost/Month** | ~$10-20 |
| **Data Throughput/Month** | ~500 MB |
| **Uptime SLA** | 99.95% (Azure) |

---

## 🔗 Integration Points

### With Syncfusion Grid (`/syncfusion` endpoint)
- Display ACE correlations in interactive grid
- Filter by risk score, entity type, source
- Export to CSV/PDF for forensic reports

### With Tasks Dashboard (`/tasks` endpoint)
- Live summary of correlation statistics
- High-risk entity alerts
- Investigation completion status

### With Maps Hub (`/maps` endpoint)
- 3D visualization of CCTV network
- OpenOSINT target node markers
- ACE correlation clusters
- Voice-controlled navigation

---

## 📚 Documentation Files

| Document | Purpose | Location |
|----------|---------|----------|
| **ACE_DEPLOYMENT_GUIDE.md** | ACE setup & configuration | Root |
| **QUICK_START.md** | Live endpoint quick links | Root |
| **ACCESS_INDEX.md** | All credentials & URLs | Root |
| **openosint_runner.py** | OpenOSINT CLI wrapper | scripts/ |
| **caltrans_d12_pull.py** | CCTV pipeline | scripts/ |
| **caltrans_d12_cctv.geojson** | Camera coordinates | evidence/ |
| **openosint_nodes.json** | Target manifest | evidence/ |

---

## 🎯 Next Steps

1. **Deploy ACE to Azure** ✅
   - `func azure functionapp publish osintneoai-ace --build remote`

2. **Run Initial Investigations** 
   - `python scripts/openosint_runner.py`

3. **View Live CCTV Network**
   - Navigate to `http://127.0.0.1:5052/maps`

4. **Monitor Correlations**
   - Check `https://osintneoai-app-949.azurewebsites.net/api/correlation/status`

5. **Customize Targets**
   - Edit `evidence/openosint_nodes.json`
   - Add/remove investigation targets

---

**System Ready for 24/7 Operation** ✅
