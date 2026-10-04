import json
import os

output_file = "badass_osint_map.html"

# Primary Nodes (Real Estate & Hubs)
nodes = [
    {"id": "HBNC", "target": "HBNC Toxic Site", "lat": 33.7064036, "lon": -117.9881801, "type": "Environmental Hazard", "color": [230, 57, 70]},
    {"id": "7561_CENTER", "target": "7561 Center Ave (Steering Hub)", "lat": 33.7317, "lon": -117.9945, "type": "Shell LLC Hub", "color": [255, 183, 3]},
    {"id": "17642_BEACH", "target": "17642 Beach Blvd (Acquisition)", "lat": 33.7060, "lon": -117.9885, "type": "Real Estate Absorption", "color": [114, 9, 183]},
    {"id": "3311_BOUNTY", "target": "3311 Bounty Cir (Stewart Ind)", "lat": 33.7320, "lon": -118.0142, "type": "$0 Transfer Layer", "color": [67, 170, 139]},
    {"id": "7100_CERRITOS", "target": "7100 Cerritos Ave (Pham LLC)", "lat": 33.8248, "lon": -118.0053, "type": "$0 Transfer Layer", "color": [67, 170, 139]},
    {"id": "CITY_HALL", "target": "City of HB / Govt Node", "lat": 33.6595, "lon": -117.9988, "type": "Government Entity", "color": [255, 255, 255]}
]

# Create Nodes GeoJSON
node_features = []
for p in nodes:
    node_features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [p["lon"], p["lat"]]
        },
        "properties": {
            "id": p["id"],
            "target": p["target"],
            "type": p["type"],
            "color": p["color"]
        }
    })

geojson_nodes = {
    "type": "FeatureCollection",
    "features": node_features
}

# Create Arcs (Maltego Relationships) GeoJSON
# These will draw glowing lines between the nodes
links = [
    {"source": "HBNC", "target": "17642_BEACH", "label": "Adjacent Expansion / Lease"},
    {"source": "CITY_HALL", "target": "HBNC", "label": "Fraudulent CEQA / RPM Contract"},
    {"source": "7561_CENTER", "target": "17642_BEACH", "label": "Grant Diversion / Absorption"},
    {"source": "7561_CENTER", "target": "3311_BOUNTY", "label": "PPP / Structuring Loop"},
    {"source": "7561_CENTER", "target": "7100_CERRITOS", "label": "$0 Conveyance Loop (Peter Pham)"}
]

arc_features = []
node_dict = {n["id"]: n for n in nodes}

for link in links:
    src = node_dict[link["source"]]
    tgt = node_dict[link["target"]]
    arc_features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [src["lon"], src["lat"]],
                [tgt["lon"], tgt["lat"]]
            ]
        },
        "properties": {
            "label": link["label"],
            "source_target": src["target"],
            "target_target": tgt["target"]
        }
    })

geojson_arcs = {
    "type": "FeatureCollection",
    "features": arc_features
}

# Kepler Configuration for infinity-pool tablet feel
kepler_config = {
  "version": "v1",
  "config": {
    "visState": {
      "filters": [],
      "layers": [
        {
          "id": "osint_nodes_layer",
          "type": "point",
          "config": {
            "dataId": "osint_nodes",
            "label": "Entity Nodes",
            "color": [255, 183, 3],
            "columns": {"lat": "lat", "lng": "lon", "altitude": None},
            "isVisible": True,
            "visConfig": {"radius": 20, "fixedRadius": False, "opacity": 0.8, "outline": False}
          }
        },
        {
          "id": "osint_links_layer",
          "type": "arc",
          "config": {
            "dataId": "osint_arcs",
            "label": "Maltego Connections",
            "color": [114, 9, 183],
            "columns": {
              "lat0": "source_lat", "lng0": "source_lon",
              "lat1": "target_lat", "lng1": "target_lon"
            },
            "isVisible": True,
            "visConfig": {"opacity": 0.8, "thickness": 3, "colorRange": {"name": "Global Warming", "type": "sequential", "category": "Uber", "colors": ["#5A1846", "#900C3F", "#C70039", "#E3611C", "#F1920E", "#FFC300"]}}
          }
        }
      ],
      "interactionConfig": {
        "tooltip": {"fieldsToShow": {"osint_nodes": ["target", "type"], "osint_arcs": ["label"]}},
        "brush": {"enabled": False}
      },
      "layerBlending": "additive",
      "splitMaps": []
    },
    "mapState": {
      "bearing": 24,
      "dragRotate": True,
      "latitude": 33.74,
      "longitude": -118.00,
      "pitch": 45,
      "zoom": 11.5,
      "isSplit": False
    },
    "mapStyle": {
      "styleType": "dark",
      "topLayerGroups": {},
      "visibleLayerGroups": {"label": True, "road": True, "border": False, "building": True, "water": True, "land": True, "3d building": True}
    }
  }
}

html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>GOLD DIGGER AI — INFINITY POOL MAP</title>
  <script src="https://unpkg.com/react@16.8.4/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@16.8.4/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/redux@3.7.2/dist/redux.js"></script>
  <script src="https://unpkg.com/react-redux@7.1.3/dist/react-redux.min.js"></script>
  <script src="https://unpkg.com/styled-components@4.1.3/dist/styled-components.min.js"></script>
  <script src="https://unpkg.com/kepler.gl@2.5.5/umd/keplergl.min.js"></script>
  <style type="text/css">
    body, html {{ margin: 0; padding: 0; overflow: hidden; height: 100vh; width: 100vw; background: #000; }}
    /* Hide the side panel by default for the infinity pool feel, but allow toggle */
    .kepler-gl__side-panel {{ opacity: 0.85; transition: opacity 0.3s; }}
    .kepler-gl__side-panel:hover {{ opacity: 1; }}
  </style>
</head>
<body>
  <div id="app"></div>
  <script>
    const reducers = (function(keplerGl, redux) {{
      return redux.combineReducers({{
        keplerGl: keplerGl.keplerGlReducer
      }});
    }})(KeplerGl, Redux);

    const store = Redux.createStore(reducers, {{}}, Redux.applyMiddleware(KeplerGl.taskMiddleware));

    const App = (function(react, keplerGl, reactRedux) {{
      var KeplerGlComponent = keplerGl.KeplerGl;
      return function() {{
        return react.createElement(
          'div',
          {{style: {{position: 'absolute', left: 0, top: 0, width: '100vw', height: '100vh'}}}},
          react.createElement(KeplerGlComponent, {{
            mapboxApiAccessToken: 'YOUR_MAPBOX_TOKEN',
            id: 'map',
            width: window.innerWidth,
            height: window.innerHeight
          }})
        );
      }}
    }})(React, KeplerGl, ReactRedux);

    const ConnectedApp = ReactRedux.connect(state => state)(App);

    ReactDOM.render(
      React.createElement(ReactRedux.Provider, {{store}}, React.createElement(ConnectedApp)),
      document.getElementById('app')
    );

    // Inject our multi-layered datasets
    setTimeout(() => {{
      const dataToLoad = [
        {{
          info: {{ label: 'Entity Nodes', id: 'osint_nodes' }},
          data: {json.dumps(geojson_nodes)}
        }},
        {{
          info: {{ label: 'Maltego Linkages', id: 'osint_arcs' }},
          data: {json.dumps(geojson_arcs)}
        }}
      ];
      
      const config = {json.dumps(kepler_config)};

      store.dispatch(KeplerGl.addDataToMap({{
        datasets: dataToLoad,
        config: config
      }}));
      
      // Auto-hide the sidebar after load to maximize map space for tablets
      setTimeout(() => {{
        store.dispatch(KeplerGl.toggleSidePanel(''));
      }}, 1500);
      
    }}, 800);
  </script>
</body>
</html>
"""

with open(output_file, "w") as f:
    f.write(html_content)

print("Tablet-optimized Kepler.gl map with Maltego overlays generated at: " + os.path.abspath(output_file))
