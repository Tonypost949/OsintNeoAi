# ARCGIS FOR TEAMS INTEGRATION GUIDE — OSINT Neo AI Spatial Targets

**Purpose:** Get the HBNC RICO spatial evidence set into ArcGIS Online, then into
Microsoft Teams as an ArcGIS tab and as Adaptive Card alerts.

**Evidence source:** `hbnc_rico_gis.html` (repo root) with chain of custody per
`hbnc-gis-v2/README.md`. Coordinates trace to Phase I ESA T10000018579, site
assessment reports, parcel exports, PPP/SBA records, and federal filings.

---

## Files in this package

| File | What it is |
|------|-----------|
| `arcgis_for_teams_geojson.geojson` | **Publish this.** 55 features (points + lines), EPSG:4326, with `Severity` (CRITICAL/HIGH/MEDIUM/INFO) and `SeverityRank` |
| `arcgis_teams_build.py` | Regenerates the .geojson, sample card, and dashboard from the raw evidence constants |
| `arcgis_teams_card_generator.py` | Converts GeoJSON → Teams Adaptive Cards (`--webhook` posts live) |
| `arcgis_teams_adaptive_card_sample.json` | Example card payload (CRITICAL: HBNC Toxic Site) |
| `arcgis_teams_dashboard.html` | Self-contained Leaflet dashboard — target list, markers, card preview |
| `arcgis_teams_cards/` | Generated output: one JSON payload per target + index CSV + combined payload |

Layer breakdown in the GeoJSON:

| Layer | Count |
|---|---|
| TOXIC | 3 |
| SINKHOLE | 4 |
| BLACKHOLE | 4 |
| LLC | 13 |
| FCA | 5 |
| CPS | 5 |
| PROCUREMENT | 5 |
| INFRA | 4 (lines) |
| PLUME | 12 (vectors) |

---

## Step 1 — Publish GeoJSON to ArcGIS Online (free, no credit needed)

1. Sign in to https://www.arcgis.com (or your org URL).
2. **Content → New Item → Your device**.
3. Upload `arcgis_for_teams_geojson.geojson`.
4. Choose **Add and create a hosted feature layer**.
5. Name it `OSINT Neo AI Spatial Targets`, **Save and Publish**.
6. Result: Hosted Feature Layer with all 55 features + `Severity` attribute, usable by
   Map Viewer, dashboards, and the ArcGIS app in Teams.
7. (Optional) **Share → Everyone (public)** if the team channel users are anonymous,
   or share with the group that contains your Teams users.

> ArcGIS Online free tier supports hosted feature layers from GeoJSON uploads.
> No ArcGIS Pro or license credits needed for this flow.

## Step 2 — Create the Web Map

1. Open the published feature layer.
2. **Open in Map Viewer**.
3. Style by field **`Severity`**:
   - CRITICAL → Red
   - HIGH → Orange
   - MEDIUM → Yellow
   - INFO → Blue
4. **Save** as `OSINT Neo AI Spatial Map`.

## Step 3 — Add the Web Map to Microsoft Teams

1. In a Teams channel: **+ → Add a tab → ArcGIS**.
2. Sign in with your ArcGIS account (same org).
3. Choose **OSINT Neo AI Spatial Map**.
4. **Save.**

Result structure:

```
Teams Channel
└── ArcGIS Tab (Saved Web Map)
    └── 55 spatial targets, severity-styled
```

## Step 4 — Use the dashboard as a Teams tab (no ArcGIS login needed)

`arcgis_teams_dashboard.html` is fully self-contained (Leaflet, dark mode,
target list, popups, adaptive-card preview, severity colors).

Host it anywhere HTTPS:

- **GitHub Pages** — push to a repo → Settings → Pages → serve from main /docs
- **Render static site** — free tier, or the existing Flask app in this repo
- **SharePoint** — upload to a site library and use the file URL
- **Azure Web App / static hosting**

Then in Teams: → **+ Add a tab → Website** → paste the URL.

## Step 5 — Push Adaptive Cards to a Teams channel (alerts)

### A. Manual (instant)

```python
python arcgis_teams_card_generator.py --severity CRITICAL
```

Generates `arcgis_teams_cards/` with one payload per CRITICAL target and
`arcgis_teams_cards_all.json`. Open any `.json`, copy to clipboard.

### B. Incoming Webhook

1. In Teams channel → **⋮ → Connectors → Incoming Webhook → Add → Configure**
   → create URL.
2. Post cards:

```python
python arcgis_teams_card_generator.py --webhook https://outlook.office.com/webhook/xxxx
```

Payload format sent: `{type:"message",attachments:[{contentType:"application/vnd.microsoft.card.adaptive",content:{...}}]}`

### C. Power Automate (alert on web map updates)

1. New flow → trigger: **ArcGIS** (Map/Feature updates) or any data change.
2. Action: **Compose** with Adaptive Card JSON from `arcgis_teams_adaptive_card_sample.json`
   or a card file in `arcgis_teams_cards/`.
3. Action: **Post message in a chat or channel** → **Post adaptive card**.

```go
Data Change (ArcGIS feature layer)
      ↓
Power Automate
      ↓
Adaptive Card JSON
      ↓
Teams channel message
```

---

## Architecture (what you now have)

```
arcgis_for_teams_geojson.geojson ──▶ ArcGIS Online ──▶ Hosted Feature Layer ──▶ Web Map ──▶ ArcGIS for Teams tab

arcgis_teams_card_generator.py ──▶ Adaptive Card JSON ──▶ Teams Webhook / Power Automate ──▶ Teams alerts

arcgis_teams_dashboard.html ──▶ any static host ──▶ Teams Website tab
```

---

## Verification

- `arcgis_teams_card_generator.py` runs end-to-end: 55 targets → 55 card files + index + combined payload + sample.
- Sample payload posts directly to Teams as `application/vnd.microsoft.card.adaptive`.
- All coordinates ≤ 6 decimals, WGS84 (EPSG:4326) — drop-in for AGOL hosted layer.

---

## Maintenance

- New evidence → add a row to the constant blocks at the top of `arcgis_teams_build.py`
  (TOXIC / LLC / FCA / CPS / PROCURE / INFRA / PLUME), then:
  `python arcgis_teams_build.py && python arcgis_teams_card_generator.py`
- Re-publish the GeoJSON in ArcGIS Online (the layer is hosted; overwrite
  by uploading the new file and replacing the item data).
- Cards live in `arcgis_teams_cards/` — regenerate after any rebuild.
- Data is tracked from the HBNC RICO evidence set (see `hbnc-gis-v2/README.md`
  chain-of-custody table). Every coordinate traces to a source document.