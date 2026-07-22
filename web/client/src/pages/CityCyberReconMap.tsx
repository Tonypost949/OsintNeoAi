/**
 * CityCyberReconMap.tsx
 * =====================
 * Interactive geographic map of geolocated municipal infrastructure nodes.
 *
 * Features:
 *  • Loads marker data from /web/client/src/data/cyber_recon_geo.json
 *    (populated by agent/fetch_geodata.py)
 *  • Renders each domain as a colored pin on a Leaflet map
 *  • Red pulsing pin  = exposed endpoint (CRITICAL)
 *  • Green pin        = live, not exposed
 *  • Grey pin         = unreachable
 *  • Click a pin → sidebar panel shows full domain details ("other listing")
 *  • Toggle between ALL markers and EXPOSED ONLY ("Strike mode")
 *  • Record button → downloads timestamped session log
 *
 * Route: /recon-map
 */

import React, { useState, useEffect, useCallback, useRef } from "react";

// ── Types ────────────────────────────────────────────────────────────────────
interface Marker {
  domain:      string;
  ip:          string;
  city:        string;
  state:       string;
  country:     string;
  lat:         number;
  lng:         number;
  status_code: number;
  is_exposed:  boolean;
  isp:         string;
  record_type: string;
}

interface GeoCache {
  generated_at:  string;
  source_table:  string;
  total:         number;
  exposed_count: number;
  markers:       Marker[];
}

// ── Static fallback data (shown while JSON loads) ────────────────────────────
const DEMO_MARKERS: Marker[] = [
  { domain: "hbpd.org",             ip: "162.242.210.88", city: "Huntington Beach", state: "CA", country: "US", lat: 33.6595, lng: -117.9988, status_code: 200, is_exposed: true,  isp: "OC Public Fiber",          record_type: "A" },
  { domain: "huntingtonbeachca.gov", ip: "162.242.210.89", city: "Huntington Beach", state: "CA", country: "US", lat: 33.6600, lng: -117.9990, status_code: 200, is_exposed: false, isp: "OC Public Fiber",          record_type: "A" },
  { domain: "santamonicapd.org",     ip: "23.21.198.44",   city: "Santa Monica",    state: "CA", country: "US", lat: 34.0195, lng: -118.4912, status_code: 200, is_exposed: true,  isp: "Westside Muni Cloud",      record_type: "A" },
  { domain: "cityofirvine.org",      ip: "192.195.82.101", city: "Irvine",          state: "CA", country: "US", lat: 33.6846, lng: -117.8265, status_code: 200, is_exposed: false, isp: "Irvine Spectrum Net",      record_type: "A" },
  { domain: "lapdonline.org",        ip: "141.218.2.10",   city: "Los Angeles",     state: "CA", country: "US", lat: 34.0522, lng: -118.2437, status_code: 200, is_exposed: true,  isp: "LA City Fiber backbone",   record_type: "A" },
  { domain: "santaanapd.org",        ip: "198.143.44.12",  city: "Santa Ana",       state: "CA", country: "US", lat: 33.7455, lng: -117.8677, status_code: 200, is_exposed: true,  isp: "Southern CA Municipal Net",record_type: "A" },
  { domain: "dallaspolice.net",      ip: "209.124.180.12", city: "Dallas",          state: "TX", country: "US", lat: 32.7767, lng: -96.7970,  status_code: 200, is_exposed: true,  isp: "Texas Public Cyber Infra", record_type: "A" },
  { domain: "newportbeachca.gov",    ip: "64.145.82.10",   city: "Newport Beach",   state: "CA", country: "US", lat: 33.6189, lng: -117.9289, status_code: 200, is_exposed: false, isp: "OC City Net",              record_type: "A" },
];

// ── Styles ───────────────────────────────────────────────────────────────────
const styles: Record<string, React.CSSProperties> = {
  page: {
    display:         "flex",
    flexDirection:   "column",
    height:          "100vh",
    background:      "#0b0e14",
    color:           "#c8d0dc",
    fontFamily:      "'Segoe UI', Tahoma, sans-serif",
    overflow:        "hidden",
  },
  header: {
    display:         "flex",
    alignItems:      "center",
    gap:             12,
    padding:         "10px 20px",
    background:      "#0f1420",
    borderBottom:    "1px solid #1f2a3a",
    flexShrink:      0,
  },
  title: {
    color:           "#7ab7ff",
    margin:          0,
    fontSize:        20,
    fontWeight:      700,
  },
  badge: {
    display:         "inline-block",
    padding:         "2px 10px",
    borderRadius:    20,
    fontSize:        12,
    fontWeight:      700,
  },
  controls: {
    display:         "flex",
    gap:             8,
    marginLeft:      "auto",
    flexWrap:        "wrap",
  },
  btn: {
    padding:         "7px 16px",
    border:          "none",
    borderRadius:    8,
    fontWeight:      600,
    fontSize:        13,
    cursor:          "pointer",
    display:         "flex",
    alignItems:      "center",
    gap:             6,
    transition:      "opacity .15s",
  },
  body: {
    display:         "flex",
    flex:            1,
    overflow:        "hidden",
  },
  mapArea: {
    flex:            1,
    position:        "relative",
    overflow:        "hidden",
    background:      "#0f1420",
  },
  sidebar: {
    width:           320,
    background:      "#141a24",
    borderLeft:      "1px solid #1f2a3a",
    overflowY:       "auto",
    padding:         16,
    flexShrink:      0,
  },
  pinLabel: {
    position:        "absolute",
    pointerEvents:   "none",
    background:      "rgba(11,14,20,.85)",
    color:           "#e0e8f0",
    padding:         "3px 8px",
    borderRadius:    6,
    fontSize:        11,
    whiteSpace:      "nowrap",
    transform:       "translate(-50%, -100%)",
    marginTop:       -6,
  },
};

// ── Tiny canvas map renderer ──────────────────────────────────────────────────
const BOUNDS = { minLat: 30, maxLat: 38, minLng: -122, maxLng: -90 };

function project(lat: number, lng: number, w: number, h: number): [number, number] {
  const x = ((lng - BOUNDS.minLng) / (BOUNDS.maxLng - BOUNDS.minLng)) * w;
  const y = ((BOUNDS.maxLat - lat) / (BOUNDS.maxLat - BOUNDS.minLat)) * h;
  return [x, y];
}

// ── Main component ────────────────────────────────────────────────────────────
const CityCyberReconMap: React.FC = () => {
  const [markers,       setMarkers]      = useState<Marker[]>(DEMO_MARKERS);
  const [meta,          setMeta]         = useState<Partial<GeoCache>>({});
  const [selected,      setSelected]     = useState<Marker | null>(null);
  const [strikeOnly,    setStrikeOnly]   = useState(false);
  const [isRecording,   setIsRecording]  = useState(false);
  const [sessionLog,    setSessionLog]   = useState<string[]>([]);
  const [tooltip,       setTooltip]      = useState<{ x: number; y: number; label: string } | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const logRef    = useRef<string[]>([]);

  // Load cache JSON
  useEffect(() => {
    fetch("/src/data/cyber_recon_geo.json")
      .then((r) => r.json())
      .then((data: GeoCache) => {
        setMarkers(data.markers);
        setMeta(data);
        appendLog(`Loaded ${data.total} markers (${data.exposed_count} exposed)`);
      })
      .catch(() => {
        appendLog("Cache not found — using demo data. Run: python agent/fetch_geodata.py");
      });
  }, []);

  // Logging
  const appendLog = useCallback((msg: string) => {
    const line = `[${new Date().toLocaleTimeString()}] ${msg}`;
    logRef.current.push(line);
    if (isRecording) {
      setSessionLog((prev) => [...prev, line]);
    }
  }, [isRecording]);

  // Download session log
  const downloadLog = () => {
    const content = logRef.current.join("\n");
    const blob    = new Blob([content], { type: "text/plain" });
    const url     = URL.createObjectURL(blob);
    const a       = document.createElement("a");
    a.href        = url;
    a.download    = `strike_session_${new Date().toISOString().slice(0, 19).replace(/[:-]/g, "")}.log`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Canvas draw
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx    = canvas.getContext("2d");
    if (!ctx) return;

    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    // Background
    ctx.fillStyle = "#0b0f1a";
    ctx.fillRect(0, 0, W, H);

    // Grid lines
    ctx.strokeStyle = "#1a2030";
    ctx.lineWidth   = 0.5;
    for (let i = 0; i <= 10; i++) {
      const x = (W / 10) * i;
      const y = (H / 10) * i;
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }

    // Draw markers
    const display = strikeOnly ? markers.filter((m) => m.is_exposed) : markers;
    for (const m of display) {
      const [x, y] = project(m.lat, m.lng, W, H);
      const r = m.is_exposed ? 9 : 6;
      const color = m.is_exposed ? "#f44336" : "#4caf50";

      // Pulse ring for exposed
      if (m.is_exposed) {
        ctx.beginPath();
        ctx.arc(x, y, r + 5, 0, Math.PI * 2);
        ctx.strokeStyle = "rgba(244,67,54,0.35)";
        ctx.lineWidth   = 2;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth   = 1;
      ctx.stroke();
    }
  }, [markers, strikeOnly]);

  // Hit test on canvas click
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width  / rect.width;
    const scaleY = canvas.height / rect.height;
    const mx     = (e.clientX - rect.left)  * scaleX;
    const my     = (e.clientY - rect.top)   * scaleY;

    const display = strikeOnly ? markers.filter((m) => m.is_exposed) : markers;
    for (const m of display) {
      const [x, y] = project(m.lat, m.lng, canvas.width, canvas.height);
      const dx     = mx - x;
      const dy     = my - y;
      const r      = m.is_exposed ? 14 : 10;
      if (dx * dx + dy * dy <= r * r) {
        setSelected(m);
        appendLog(`Selected: ${m.domain} (${m.city}, ${m.state}) — Exposed: ${m.is_exposed}`);
        return;
      }
    }
    setSelected(null);
  };

  // Hover tooltip
  const handleCanvasMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect   = canvas.getBoundingClientRect();
    const scaleX = canvas.width  / rect.width;
    const scaleY = canvas.height / rect.height;
    const mx     = (e.clientX - rect.left) * scaleX;
    const my     = (e.clientY - rect.top)  * scaleY;
    const display = strikeOnly ? markers.filter((m) => m.is_exposed) : markers;
    for (const m of display) {
      const [x, y] = project(m.lat, m.lng, canvas.width, canvas.height);
      const dx = mx - x;
      const dy = my - y;
      if (dx * dx + dy * dy <= 200) {
        const cx = (x / canvas.width)  * rect.width  + rect.left;
        const cy = (y / canvas.height) * rect.height + rect.top;
        setTooltip({ x: e.clientX, y: e.clientY, label: `${m.domain} — ${m.city}` });
        return;
      }
    }
    setTooltip(null);
  };

  const exposed = markers.filter((m) => m.is_exposed);

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>🗺️ Strike Map</h1>
        <span style={{ ...styles.badge, background: "#1b3a1b", color: "#4caf50" }}>
          {markers.length} nodes
        </span>
        <span style={{ ...styles.badge, background: "#3a1b1b", color: "#f44336" }}>
          {exposed.length} exposed
        </span>
        {meta.generated_at && (
          <span style={{ fontSize: 11, color: "#556" }}>
            Cache: {new Date(meta.generated_at).toLocaleString()}
          </span>
        )}
        <div style={styles.controls}>
          <button
            style={{ ...styles.btn, background: strikeOnly ? "#b71c1c" : "#2a3344", color: "#fff" }}
            onClick={() => setStrikeOnly(!strikeOnly)}
          >
            {strikeOnly ? "🎯 Strike Only" : "🌐 All Nodes"}
          </button>
          <button
            style={{ ...styles.btn, background: isRecording ? "#b71c1c" : "#2a3344", color: "#fff" }}
            onClick={() => {
              setIsRecording(!isRecording);
              appendLog(isRecording ? "⏹ Recording stopped" : "🔴 Recording started");
            }}
          >
            {isRecording ? "⏹ Stop" : "⏺ Record"}
          </button>
          <button
            style={{ ...styles.btn, background: "#1a6bff", color: "#fff" }}
            onClick={downloadLog}
          >
            ⬇ Receipt
          </button>
        </div>
      </div>

      {/* Body */}
      <div style={styles.body}>
        {/* Map canvas */}
        <div style={styles.mapArea}>
          <canvas
            ref={canvasRef}
            width={1200}
            height={600}
            style={{ width: "100%", height: "100%", cursor: "crosshair" }}
            onClick={handleCanvasClick}
            onMouseMove={handleCanvasMove}
            onMouseLeave={() => setTooltip(null)}
          />
          {/* Tooltip */}
          {tooltip && (
            <div
              style={{
                position:  "fixed",
                left:      tooltip.x + 12,
                top:       tooltip.y - 8,
                background:"rgba(11,14,20,.92)",
                color:     "#e0e8f0",
                padding:   "4px 10px",
                borderRadius: 6,
                fontSize:  12,
                pointerEvents: "none",
                zIndex:    999,
                border:    "1px solid #2a3344",
              }}
            >
              {tooltip.label}
            </div>
          )}
        </div>

        {/* Sidebar — the "other listing" */}
        <div style={styles.sidebar}>
          {selected ? (
            <>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <strong style={{ color: "#7ab7ff", fontSize: 15 }}>{selected.domain}</strong>
                <button
                  style={{ background: "#2a3344", border: "none", color: "#fff", borderRadius: 6, padding: "4px 10px", cursor: "pointer" }}
                  onClick={() => setSelected(null)}
                >✕</button>
              </div>

              {selected.is_exposed && (
                <div style={{ background: "#3a1b1b", color: "#f44336", padding: "6px 10px", borderRadius: 6, marginBottom: 10, fontSize: 12, fontWeight: 700 }}>
                  ⚠️ EXPOSED ENDPOINT
                </div>
              )}

              {[
                ["IP",          selected.ip],
                ["City",        selected.city],
                ["State",       selected.state],
                ["Country",     selected.country],
                ["ISP",         selected.isp],
                ["Record Type", selected.record_type],
                ["Status Code", selected.status_code],
                ["Lat/Lng",     `${selected.lat.toFixed(4)}, ${selected.lng.toFixed(4)}`],
              ].map(([k, v]) => (
                <div key={String(k)} style={{ marginBottom: 8 }}>
                  <span style={{ color: "#8895aa", fontSize: 11 }}>{k}</span>
                  <div style={{ fontFamily: "monospace", fontSize: 13, color: "#e0e8f0", wordBreak: "break-all" }}>
                    {String(v)}
                  </div>
                </div>
              ))}

              <div style={{ marginTop: 12, paddingTop: 12, borderTop: "1px solid #1f2a3a" }}>
                <div style={{ fontSize: 11, color: "#8895aa", marginBottom: 6 }}>BigQuery Query</div>
                <pre style={{ background: "#0b0e14", padding: 8, borderRadius: 6, fontSize: 11, color: "#7ab7ff", overflowX: "auto" }}>
{`SELECT *
FROM \`project-743aab84-f9a5-4ec7-954
  .national_audits
  .ip_geolocation_index\`
WHERE domain = '${selected.domain}'`}
                </pre>
              </div>
            </>
          ) : (
            <div style={{ color: "#4a5568", fontSize: 13 }}>
              <p>👈 Click a node to see the full listing.</p>
              <p style={{ marginTop: 12 }}>
                <span style={{ color: "#f44336" }}>●</span> Red = exposed<br />
                <span style={{ color: "#4caf50" }}>●</span> Green = live, safe<br />
                <span style={{ color: "#555" }}>●</span> Grey = unreachable
              </p>
              <p style={{ marginTop: 16, fontSize: 11 }}>
                Total: <strong style={{ color: "#c8d0dc" }}>{markers.length}</strong><br />
                Exposed: <strong style={{ color: "#f44336" }}>{exposed.length}</strong>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CityCyberReconMap;
