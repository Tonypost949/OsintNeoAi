# Actionable Task List: God's Eye View Spatial Intelligence (todo.md)

## Phase 1: Real-Time Telemetry Stream & Historical Trajectory Scrubber

### Task 1: GPS Trajectory Extractor & Time-Series Formatter
**Description:** Parse GPS logs from `edr_all_gps_coordinates.json` and generate a structured GeoJSON track file `public/gps_trajectory_stream.geojson` with time-ordered coordinates.
**Acceptance Criteria:**
- [x] Reads GPS latitude/longitude entries across Orange County patrol corridor.
- [x] Formats output as GeoJSON Feature with geometry type `LineString` and `Point` milestones.
**Verification:**
- [x] Tested `transforms/extract_gps_tracks.py` -> 10 trajectory features exported to `public/gps_trajectory_stream.geojson`.
**Files touched:**
- `transforms/extract_gps_tracks.py`
- `public/gps_trajectory_stream.geojson`

---

### Task 2: God's Eye Interactive Time-Slider HUD Control
**Description:** Add an interactive timeline scrubber and animated trajectory playback to `gods_eye_view.html` using Leaflet playback/polyline animations.
**Acceptance Criteria:**
- [x] Time slider allows scrubbing through historical waypoints (0 to 8).
- [x] Play/Pause button animates movement along the trajectory line with live speed badge.
**Verification:**
- [x] Verified `gods_eye_view.html` timeline controls and waypoint stepper.
**Files touched:**
- `gods_eye_view.html`

---

## Checkpoint 1: Trajectory Engine
- [x] Trajectory stream generated cleanly
- [x] Playback scrubber functional in God's Eye View

---

## Phase 2: OpenOSINT Entity Inspector Popups & HUD Enrichment

### Task 3: Live Entity Inspector API Route in `simple_map_server.py`
**Description:** Add `/api/inspect` endpoint to `simple_map_server.py` that matches a selected location or entity name against `data/extracted_evidence_entities.json` and returns linked legal records.
**Acceptance Criteria:**
- [x] GET `/api/inspect?query=...` returns matched evidence records with SHA-256 hashes and docket numbers.
- [x] Returns structured JSON with CORS headers.
**Verification:**
- [x] Verified `http://localhost:10000/api/inspect?query=cameron` returns 15 matches with 200 OK.
**Files touched:**
- `simple_map_server.py`

---

### Task 4: HUD Entity Dossier Modal in `gods_eye_view.html`
**Description:** Implement an interactive slide-out HUD drawer in `gods_eye_view.html` displaying matched entity details, monetary amounts, and document links when a marker is clicked.
**Acceptance Criteria:**
- [x] Clicking any map pin opens HUD dossier panel.
- [x] Displays live metadata (category, coordinates, evidence mentions).
**Verification:**
- [x] Tested pin click event handler with live `/api/inspect` fetch integration.
**Files touched:**
- `gods_eye_view.html`

---

## Checkpoint 2: Intelligence Popups
- [x] Inspector API route operational (Port 10000)
- [x] HUD dossier drawer loads real-time metadata

---

## Phase 3: 3D MapLibre Extrusions & Multi-Layer GIS Overlays

### Task 5: 3D Vector Building Extrusions & Parcel Boundaries
**Description:** Embed 3D vector building height layers and Orange County municipal parcel boundaries into `maplibre_3d_tactical.html`.
**Acceptance Criteria:**
- [x] 3D building polygon extrusions render with pitch/bearing angle controls.
- [x] Direct navigation link integrated into God's Eye View top HUD.
**Verification:**
- [x] Verified route `/map/3d` in `simple_map_server.py`.
**Files touched:**
- `maplibre_3d_tactical.html`

---

### Task 6: Multi-Layer Satellite & Tactical Filter HUD
**Description:** Add quick filter toggle buttons (Thermal, Surveillance, Municipal, Corporate) to the top HUD in `gods_eye_view.html`.
**Acceptance Criteria:**
- [x] Clicking filter toggles (ALL, SURVEILLANCE, MUNICIPAL, CORPORATE) shows/hides corresponding category markers.
- [x] Active layer badges reflect current visual state.
**Verification:**
- [x] Tested category filter handlers in `gods_eye_view.html`.
**Files touched:**
- `gods_eye_view.html`

---

## Final Checkpoint: Complete Verification
- [x] All 6 tasks completed and tested
- [x] All changes committed and pushed to `origin/main`
