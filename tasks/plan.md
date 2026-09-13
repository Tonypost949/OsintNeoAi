# Implementation Plan: God's Eye View Next-Gen Spatial Intelligence & Real-Time Telemetry

## Overview
This plan upgrades the [God's Eye View](http://localhost:10000/map/godseye) reconnaissance cockpit into a real-time tactical intelligence dashboard with animated trajectory playback, AI entity inspector popups powered by [tools/openosint_mcp_server.py](file:///C:/OsintNeoAi/tools/openosint_mcp_server.py), and 3D building extrusions.

---

## Architecture Flow (<50 Columns)

```
┌────────────────────────────────────────────────────────┐
│  1. GPS / Takeout / EXIF Telemetry Streams             │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  2. Live GeoJSON Transformer & Socket Streamer         │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  3. God's Eye Tactical Cockpit (Port 10000)            │
│     • Animated Path Trajectory Playback                │
│     • 3D Building Extrusions (MapLibre GL)             │
│     • OpenOSINT AI Entity Inspector Popup              │
└────────────────────────────────────────────────────────┘
```

---

## Architecture Decisions
- **Decoupled Telemetry**: Location streams feed into `public/live_telemetry.geojson` with time-stamped waypoints, allowing front-end animation scrubbers to replay historical movement chronologically.
- **Dynamic Entity Enrichment**: Clicking a marker queries the OpenOSINT API route (`/api/inspect_entity`) to display real-time intelligence cards directly inside the HUD overlay.
- **Hybrid 2D/3D Rendering**: Seamless toggle between lightweight Leaflet satellite tiles and GPU-accelerated MapLibre 3D vector extrusions.

---

## Task List

### Phase 1: Real-Time Telemetry Stream & Historical Trajectory Scrubber
- [ ] **Task 1: GPS Trajectory Extractor & Time-Series Formatter**
  - Extract chronologically ordered waypoints from `edr_all_gps_coordinates.json` into a GeoJSON `FeatureCollection` of `LineString` tracks with timestamp metadata.
- [ ] **Task 2: God's Eye Interactive Time-Slider HUD Control**
  - Add playback timeline scrubber to `gods_eye_view.html` to animate target movements over time.

#### Checkpoint 1: Trajectory Engine
- [ ] Historical waypoints animate smoothly on map without frame drops.
- [ ] Time slider controls timeline playback accurately.

---

### Phase 2: OpenOSINT Entity Inspector Popups & HUD Enrichment
- [ ] **Task 3: Live Entity Inspector API Route in `simple_map_server.py`**
  - Add `/api/inspect` endpoint that connects marker coordinates to extracted evidence ledger records in `data/extracted_evidence_entities.json`.
- [ ] **Task 4: HUD Entity Dossier Modal in `gods_eye_view.html`**
  - Create interactive sidepanel displaying legal dockets, monetary amounts, and target emails upon marker click.

#### Checkpoint 2: Intelligence Popups
- [ ] Clicking map marker displays full extracted entity dossier.
- [ ] Zero latency (< 50ms) retrieval from local evidence ledger.

---

### Phase 3: 3D MapLibre Extrusions & Multi-Layer GIS Overlays
- [ ] **Task 5: 3D Vector Building Extrusions & Parcel Boundaries**
  - Integrate MapLibre 3D building height layers and municipal parcel boundary polygons.
- [ ] **Task 6: Multi-Layer Satellite & Tactical Filter HUD**
  - Add instant toggles for Thermal/Surveillance, Municipal Utilities, Court Venues, and Commercial Entities.

#### Checkpoint 3: Complete Cockpit Upgrade
- [ ] 3D buildings extrude cleanly with hardware acceleration.
- [ ] All code committed and pushed to `origin/main`.

---

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Large trajectory datasets lagging the browser | Medium | Chunk waypoints into GeoJSON MultiLineString with simplified geometry |
| Missing WebGL support on legacy hardware | Low | Automatic fallback to 2D Leaflet raster tiles |
