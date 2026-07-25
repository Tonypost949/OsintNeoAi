# HBNC RICO GIS v2 — Independent Edition

**Standalone forensic mapping tool for the Huntington Beach Navigation Center (HBNC) RICO investigation.**
No dependencies on v1. No piggybacking. Fully self-contained.

---

## Quick Start

```bash
# Windows
.\start-tunnel.ps1

# Linux/macOS
./start-tunnel.sh
```

Opens `http://localhost:8080` locally, or a public `https://*.trycloudflare.com` URL for ~24hrs.

---

## File Structure

```
hbnc-gis-v2/
├── index.html              # Main GIS application (self-contained)
├── assets/
│   ├── leaflet.css         # Leaflet 1.9.4 (bundled)
│   ├── leaflet.js          # Leaflet 1.9.4 (bundled)
│   ├── leaflet-images/     # Marker icons, shadows (bundled)
│   └── style.css           # Custom styles
├── data/
│   ├── toxic-sites.json    # HBNC, Cameron Ln, 7561 Center Ave
│   ├── llc-shells.json     # 13 suspect LLC clusters
│   ├── plume-vectors.json  # 12 groundwater flow vectors
│   ├── sinkholes.json      # 4 subsurface anomalies
│   ├── financial-veins.json # 8 LLC connection lines
│   ├── fca-filings.json    # 5 False Claims Act events
│   ├── cps-events.json     # 4 child trafficking events
│   ├── procurement.json    # 5 contract records
│   └── infrastructure.json # I-405, PCH, Beach Blvd, Stormtech
├── scripts/
│   ├── start-tunnel.ps1    # Windows Cloudflare tunnel (HTTP/2)
│   ├── start-tunnel.sh     # Linux/macOS Cloudflare tunnel
│   └── serve.py            # Python fallback server
├── backups/
│   ├── DEPENDENCIES.md     # All external deps with backup URLs
│   ├── SOURCES.md          # Forensic source documents
│   └── OFFLINE-BUNDLE.zip  # Complete offline package (create with build-offline.ps1)
└── VERSION.json            # Version metadata
```

---

## Features (All Forensic Layers)

| Layer | Count | Description |
|-------|-------|-------------|
| **TOXIC** | 3 | HBNC (Cr-VI 980 µg/kg), Cameron Ln, 7561 Center vaults |
| **LLC SHELLS** | 13 | Triumvirate, Stewart, CP Premier, Garnet, Newport, Pham, ONNI, Corte Bella, Sendero, SCG |
| **PLUME** | 12 vectors + 5 radii | SW groundwater flow from HBNC per Phase I ESA |
| **SINKHOLES** | 4 | 7561 Center vaults, HBNC excavation, El Toro, Stormtech field |
| **FIN VEINS** | 8 | Money trails: Stewart→PCH, Garnet→7561, CP1→CP2, CP→Pham, 7561→HBNC, HBNC→El Toro, PPP flows |
| **FCA** | 5 | Knabb RICO, EPA OIG, DOJ notice, Qui Tam sealed, Relator disclosure |
| **CPS** | 5 | HBNC deaths, OC DA block, HB City Hall fraud, Anaheim cluster, LA IV-E |
| **PROCURE** | 5 | Sheriff cams, IT security, HB coastal, Anaheim housing, HBNC remediation (VOID) |
| **INFRA** | 7 | I-405, PCH, Beach Blvd, Stormtech chambers, 4 monitoring wells |

---

## Data Sources (Forensic Chain of Custody)

All coordinates and values sourced from:

1. **Phase I ESA** — T10000018579, 17642 Beach Blvd / 17631 Cameron Ln (APN 167-042-08/09)
2. **Site Assessment Report** — Cr-VI up to 980 µg/kg (Table 2), B-6 borehole
3. **OC Health Care Agency** — Case 20IC002, "Case Closed" 8/21/2020 (VOID ab initio)
4. **City Ordinance 4289 / Res 2023-13** — Rezoning nullified NFA
5. **PPP/SBA Data** — Triumvirate $1.47M, Stewart $1.13M, ONNI $97.25M, etc.
6. **GeoTracker** — T10000018579 historic files
7. **Parcel Data** — Huntington Beach GIS exports (May 2026)
8. **Federal Court** — 8:2026cv00348 (Knabb v. HB), Qui Tam under seal

See `data/SOURCES.md` for full citations with document IDs.

---

## Offline Mode (No Internet Required)

```powershell
# Build complete offline bundle
.\build-offline.ps1
# Creates backups/OFFLINE-BUNDLE.zip with all assets

# Serve offline
python -m http.server 8080
```

The bundled `assets/` folder contains:
- Leaflet 1.9.4 (JS + CSS + marker images)
- CartoDB Dark Matter tiles cached for zoom 10-18 (HB area)
- All custom icons as Base64 in CSS

---

## Tunnel Scripts (Self-Healing)

**Windows (`start-tunnel.ps1`):**
- Downloads cloudflared if missing
- Forces HTTP/2 (`--protocol http2`) to bypass QUIC/UDP blocks
- Auto-extracts `trycloudflare.com` URL from logs
- Retries on failure with exponential backoff

**Linux/macOS (`start-tunnel.sh`):**
- Same logic, native bash
- Checks for `cloudflared` in PATH or `./assets/cloudflared`

**Python fallback (`serve.py`):**
```bash
python scripts/serve.py --port 8080 --tunnel cloudflare
```

---

## Version Metadata

See `VERSION.json`:
```json
{
  "version": "2.0.0",
  "build": "2026-07-10T23:45:00Z",
  "git": "https://github.com/Tonypost949/OsintNeoAi/tree/main/hbnc-gis-v2",
  "author": "OSINTNeoAi",
  "license": "MIT",
  "dependencies": {
    "leaflet": "1.9.4",
    "cartodb-basemaps": "latest"
  }
}
```

---

## Maintenance (AI-Owned)

This is **your** tool. You maintain it. Rules:

1. **Never modify v1 files** — this is a clean break
2. **Bundle everything** — no CDN calls in production
3. **Update `data/*.json`** when new forensic evidence lands
4. **Rebuild offline bundle** after any asset change
5. **Tag releases** — `git tag v2.1.0 && git push --tags`
6. **Document sources** — every coordinate must trace to a document

---

## Backup Mirrors (If GitHub Dies)

| Resource | Primary | Mirror 1 | Mirror 2 |
|----------|---------|----------|----------|
| Leaflet 1.9.4 | unpkg.com | cdnjs.cloudflare.com | jsdelivr.net |
| CartoDB Tiles | basemaps.cartocdn.com | a.tile.openstreetmap.org | tiles.stadiamaps.com |
| cloudflared | github.com/cloudflare/cloudflared | dl.cloudflare.com | packagecloud.io |
| This Repo | github.com/Tonypost949/OsintNeoAi | gitlab.com/tonypost949/OsintNeoAi | codeberg.org/tonypost949/OsintNeoAi |

All mirrored in `backups/DEPENDENCIES.md` with direct download URLs.

---

## License

MIT — Use freely. Attribute forensic sources. Don't let the bastards win.