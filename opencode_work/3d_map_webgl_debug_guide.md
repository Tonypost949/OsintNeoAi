# 3D Map / WebGL Debug Guide

## 1. How to Tilt the Map

You generally can't force tilt from DevTools alone unless the map app exposes a tilt API.

Inspect what map object exists:

```js
window.map
console.dir(window.map)
```

Look for methods such as:
- `setPitch`
- `setBearing`
- `flyTo`
- `rotate`
- `setView`

### Mapbox GL examples:

```js
map.setPitch(60);
map.setBearing(45);
```

### Leaflet

Leaflet by itself does not support true tilt. Tilt may be provided by:
- Leaflet.Glify
- Leaflet.MapboxGL
- Three.js overlays
- OSM Buildings
- A custom WebGL engine

If none expose tilt controls, there may be a UI button instead.

---

## 2. Errors Indicating 3D Plugin Failure

### Plugin missing

```
THREE is not defined
OSMBuildings is not defined
L.glify is not defined
L.mapboxGL is not a function
```

### Script failed to load

```
Failed to load resource
404 Not Found
net::ERR_CONNECTION_REFUSED
```

### Initialization failure

```
Uncaught TypeError
Cannot read properties of undefined
Cannot read property 'addTo' of undefined
Cannot call method on undefined
```

### WebGL failure

```
WebGL not supported
Failed to create WebGL context
THREE.WebGLRenderer error
```

---

## 3. How to Verify Tile Server Requests

Open: **F12 > Network**

1. Check **Preserve Log**
2. Refresh page
3. Filter by: `tile`, `png`, or `jpg`

Look for URLs like:
- `tile.openstreetmap.org`
- `api.mapbox.com`
- `server.arcgisonline.com`

### Healthy tile requests

- Status: `200 OK`
- Response Type: `image/png` or `image/jpeg`
- Preview tab shows actual map imagery

### Bad tile requests

| Status | Meaning |
|--------|---------|
| `404 Not Found` | Wrong URL |
| `403 Forbidden` | Authentication/API-key problem |
| `429 Too Many Requests` | Rate-limited |
| `500 Internal Server Error` | Server problem |

---

## 4. Fast Verification Commands

```js
console.table({
  Leaflet: !!window.L,
  ThreeJS: !!window.THREE,
  WebGL: !!window.WebGLRenderingContext,
  Map: !!window.map,
  Waypoints: typeof window.flightWaypoints
});
```

Check canvas elements:

```js
document.querySelectorAll("canvas").length
```

A good sign:

```js
!!window.THREE === true  // combined with
document.querySelector("canvas")  // returning a canvas element
// and no WebGL errors in Console
```

This strongly suggests the 3D engine has loaded successfully.
