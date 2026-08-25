/**
 * OSINTNeoAi GIS Map Diagnostic
 * Paste this entire script into browser DevTools Console (F12)
 * Will test all 7 levels of functionality
 */

console.log("🔍 OSINTNeoAi Tactical GIS Diagnostic v1.0\n");

// LEVEL 1: Library Detection
console.log("═══ LEVEL 1: 3D/GIS Libraries ═══");
const libs = {
  "Leaflet (L)": !!window.L,
  "Leaflet Fullscreen": !!window.L?.Control?.Fullscreen,
  "THREE.js": !!window.THREE,
  "Cesium": !!window.Cesium,
  "Mapbox GL": !!window.mapboxgl,
};
console.table(libs);

// LEVEL 2: Map Object
console.log("\n═══ LEVEL 2: Map Instance ═══");
const mapStatus = {
  "Map object exists": typeof window.map,
  "Map is Leaflet": window.map instanceof L.Map,
  "Map center": window.map?.getCenter(),
  "Map zoom": window.map?.getZoom(),
  "Map bounds": window.map?.getBounds(),
};
console.table(mapStatus);

// LEVEL 3: Autopilot & Flight Data
console.log("\n═══ LEVEL 3: Autopilot Engine ═══");
const autopilot = {
  "flightWaypoints exists": typeof window.flightWaypoints,
  "flightWaypoints length": Array.isArray(window.flightWaypoints) ? window.flightWaypoints.length : "N/A",
  "toggleAutopilot function": typeof window.toggleAutopilot,
  "flyToWaypoint function": typeof window.flyToWaypoint,
  "nextFlightWaypoint function": typeof window.nextFlightWaypoint,
};
console.table(autopilot);

if (Array.isArray(window.flightWaypoints)) {
  console.log("\n📍 First 3 Waypoints:");
  window.flightWaypoints.slice(0, 3).forEach((wp, i) => {
    console.log(`  ${i+1}. ${wp.name} @ [${wp.center[0].toFixed(4)}, ${wp.center[1].toFixed(4)}] zoom=${wp.zoom}`);
  });
}

// LEVEL 4: Layer Groups
console.log("\n═══ LEVEL 4: GIS Layer Groups ═══");
const layers = {
  "layerSuperfund": typeof window.layerSuperfund,
  "layerParcels": typeof window.layerParcels,
  "layerWells": typeof window.layerWells,
  "layerBuckRanch": typeof window.layerBuckRanch,
  "layerNevada": typeof window.layerNevada,
  "layerNationwide": typeof window.layerNationwide,
};
console.table(layers);

// LEVEL 5: Tile Layers
console.log("\n═══ LEVEL 5: Tile Servers ═══");
const tiles = {
  "ESRI Clarity": typeof window.esriClarity,
  "ESRI World Imagery": typeof window.esriSat,
  "CartoDB Dark Matter": typeof window.darkMatter,
  "OpenHistoricalMap": typeof window.openHistorical,
  "Topographic": typeof window.topoMap,
};
console.table(tiles);

// LEVEL 6: Event Handlers
console.log("\n═══ LEVEL 6: Event Listeners ═══");
const handlers = {
  "mousemove handler": !!map._events?.mousemove,
  "zoomend handler": !!map._events?.zoomend,
  "zoom level display": document.getElementById("zoom-level")?.textContent,
  "coord display": document.getElementById("mouse-coords")?.textContent,
};
console.table(handlers);

// LEVEL 7: DOM Elements
console.log("\n═══ LEVEL 7: UI Components ═══");
const dom = {
  "Map container": !!document.getElementById("map"),
  "HUD panel": !!document.getElementById("hud-panel"),
  "Autopilot bar": !!document.getElementById("autopilot-bar"),
  "Cockpit jump": !!document.getElementById("cockpit-jump"),
  "Coord HUD": !!document.getElementById("coord-hud"),
  "Autopilot button": !!document.getElementById("btn-autopilot"),
};
console.table(dom);

// LEVEL 8: Network Requests Check
console.log("\n═══ LEVEL 8: Resource Loading ═══");
const resources = {
  "Leaflet CSS loaded": !!document.querySelector("link[href*='leaflet']"),
  "Fullscreen CSS loaded": !!document.querySelector("link[href*='fullscreen']"),
  "Active base layer": window.map?.baseLayer || "Check layer control",
  "Active overlays": Object.keys(window.overlayMaps || {}).length,
};
console.table(resources);

// LEVEL 9: Functional Tests
console.log("\n═══ LEVEL 9: Functionality Tests ═══");
console.log("To run manual tests, paste these commands:");
console.log("\n  // Test 1: Fly to first waypoint");
console.log("  flyToWaypoint(0)");
console.log("\n  // Test 2: Start autopilot");
console.log("  toggleAutopilot()");
console.log("\n  // Test 3: Get current map view");
console.log("  JSON.stringify({center: map.getCenter(), zoom: map.getZoom()})");
console.log("\n  // Test 4: List all markers");
console.log("  Object.keys(window).filter(k => k.startsWith('layer')).map(k => ({[k]: window[k].getLayers().length}))");

// FINAL SUMMARY
console.log("\n═══ SUMMARY ═══");
const summary = {
  "✅ Server responds": true,
  "✅ Leaflet loaded": !!window.L,
  "✅ Map object created": typeof window.map !== 'undefined',
  "✅ Autopilot available": typeof window.toggleAutopilot === 'function',
  "⚠️  3D rendering": "Manual verification required",
};
console.table(summary);

console.log("\n🎯 Next Steps:");
console.log("1. If all above show ✅, the stack is initialized");
console.log("2. Click 'START CINEMATIC FLIGHT' button to test autopilot");
console.log("3. Check for console errors (red text)");
console.log("4. Check Network tab (F12 → Network) for failed requests");
console.log("5. Paste output of console.table() above into GitHub issue");
