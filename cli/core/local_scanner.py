import socket
import platform
import os
import sys
import shutil
import json
import urllib.request
import subprocess

def scan_local_system(root_dir=None):
    """
    Scans the local host machine telemetry, network interfaces,
    installed developer CLIs, and available intelligence maps.
    """
    if not root_dir:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    hostname = socket.gethostname()
    os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
    py_ver = platform.python_version()

    # Local IP detection
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        try:
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            pass

    # Geolocation and Public IP scan
    geo_data = {
        "public_ip": "Unknown",
        "city": "Unknown",
        "region": "Unknown",
        "country": "Unknown",
        "lat": 33.6595,
        "lon": -117.9988,
        "isp": "Local Loopback"
    }
    try:
        req = urllib.request.Request(
            "http://ip-api.com/json/",
            headers={"User-Agent": "OSINTNeoAi-LocalScanner/1.0"}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            res = json.loads(response.read().decode())
            if res.get("status") == "success":
                geo_data["public_ip"] = res.get("query", "Unknown")
                geo_data["city"] = res.get("city", "Unknown")
                geo_data["region"] = res.get("regionName", "Unknown")
                geo_data["country"] = res.get("country", "Unknown")
                geo_data["lat"] = float(res.get("lat", 33.6595))
                geo_data["lon"] = float(res.get("lon", -117.9988))
                geo_data["isp"] = res.get("isp", "Unknown")
    except Exception:
        pass

    # Installed CLIs scan
    known_clis = [
        {"name": "Google Cloud (gcloud)", "cmd": "gcloud"},
        {"name": "BigQuery (bq)", "cmd": "bq"},
        {"name": "Cloud Storage (gsutil)", "cmd": "gsutil"},
        {"name": "GitHub CLI (gh)", "cmd": "gh"},
        {"name": "Git", "cmd": "git"},
        {"name": "Docker", "cmd": "docker"},
        {"name": "Kubernetes (kubectl)", "cmd": "kubectl"},
        {"name": "Terraform", "cmd": "terraform"},
        {"name": "Node.js", "cmd": "node"},
        {"name": "Python", "cmd": "python3" if shutil.which("python3") else "python"},
        {"name": "Antigravity CLI (agy)", "cmd": "agy"}
    ]
    cli_status = []
    for c in known_clis:
        p = shutil.which(c["cmd"])
        cli_status.append({
            "name": c["name"],
            "cmd": c["cmd"],
            "installed": bool(p),
            "path": p or "Not in PATH"
        })

    # Scan available maps on disk
    map_files = []
    for f in os.listdir(root_dir):
        if f.endswith(".html") and any(k in f.lower() for k in ["map", "gis", "tactical", "swipe", "3d", "dashboard"]):
            map_files.append({
                "filename": f,
                "name": f.replace(".html", "").replace("_", " ").title(),
                "url": f"/maps/{f}"
            })

    return {
        "hostname": hostname,
        "os": os_info,
        "python": py_ver,
        "local_ip": local_ip,
        "geo": geo_data,
        "clis": cli_status,
        "maps": map_files
    }

def generate_local_system_map_html(telemetry):
    """
    Renders an interactive Tactical Map HTML centering on the user's
    local workstation node with connection vectors to targets.
    """
    lat = telemetry["geo"]["lat"]
    lon = telemetry["geo"]["lon"]
    host = telemetry["hostname"]
    pub_ip = telemetry["geo"]["public_ip"]
    loc_ip = telemetry["local_ip"]
    city = telemetry["geo"]["city"]
    region = telemetry["geo"]["region"]
    isp = telemetry["geo"]["isp"]
    os_name = telemetry["os"]

    clis_html = "".join([
        f'''<div class="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800 text-xs">
            <span class="font-bold text-white">{c["name"]}</span>
            <span class="px-2 py-0.5 rounded font-mono text-[10px] { "bg-emerald-500/20 text-emerald-400" if c["installed"] else "bg-slate-800 text-slate-500" }">{ "🟢 Ready" if c["installed"] else "⚪ Missing" }</span>
        </div>'''
        for c in telemetry["clis"]
    ])

    maps_html = "".join([
        f'''<a href="{m["url"]}" target="_blank" class="block p-2.5 rounded bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/50 transition text-xs">
            <div class="font-bold text-cyan-300 flex items-center justify-between">
                <span>{m["name"]}</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[10px] text-slate-500"></i>
            </div>
            <div class="text-[10px] font-mono text-slate-500 mt-0.5">{m["filename"]}</div>
        </a>'''
        for m in telemetry["maps"]
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OSINTNeoAi — Local System Tactical Command Map</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Manrope', sans-serif; background-color: #060913; color: #e2e8f0; }}
    .font-mono {{ font-family: 'DM Mono', monospace; }}
    #map {{ height: 100%; width: 100%; background: #080d1a; }}
    .pulse-ring {{
      border: 3px solid #00f0ff;
      border-radius: 50%;
      height: 34px;
      width: 34px;
      position: absolute;
      left: -17px;
      top: -17px;
      animation: pulsate 1.8s ease-out infinite;
      opacity: 0.8;
      pointer-events: none;
    }}
    @keyframes pulsate {{
      0% {{ transform: scale(0.1, 0.1); opacity: 0.0; }}
      50% {{ opacity: 1; }}
      100% {{ transform: scale(2.2, 2.2); opacity: 0.0; }}
    }}
  </style>
</head>
<body class="h-screen flex flex-col overflow-hidden">
  <!-- Top Bar -->
  <header class="h-14 bg-slate-900/90 border-b border-slate-800 px-6 flex items-center justify-between shrink-0 z-10">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded-lg bg-cyan-600 flex items-center justify-center text-white text-sm shadow-lg shadow-cyan-600/30">
        <i class="fa-solid fa-radar"></i>
      </div>
      <div>
        <h1 class="text-sm font-bold text-white tracking-wide uppercase">Local Host Intelligence Node // {host}</h1>
        <p class="text-[10px] text-cyan-400 font-mono">IP: {pub_ip} (Local: {loc_ip}) • Location: {city}, {region}</p>
      </div>
    </div>
    <div class="flex items-center gap-3">
      <a href="/" class="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold px-3 py-1.5 rounded-lg transition">
        <i class="fa-solid fa-terminal"></i> CLI Hub
      </a>
      <a href="/maps" class="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition">
        <i class="fa-solid fa-map"></i> Tactical Maps
      </a>
      <a href="/victims-board" class="bg-red-950/60 border border-red-500/30 text-red-300 text-xs font-bold px-3 py-1.5 rounded-lg transition">
        <i class="fa-solid fa-bullhorn"></i> Victims Board
      </a>
    </div>
  </header>

  <!-- Main Workspace -->
  <div class="flex-1 flex overflow-hidden">
    <!-- Left Sidebar: Local PC Telemetry -->
    <aside class="w-80 bg-slate-950/90 border-r border-slate-800 p-4 space-y-4 overflow-y-auto shrink-0">
      <!-- System Specs -->
      <div class="bg-slate-900/60 border border-slate-800 rounded-xl p-3.5 space-y-2.5">
        <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
          <span><i class="fa-solid fa-server text-cyan-400"></i> Workstation Specs</span>
          <span class="text-[9px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-mono">ONLINE</span>
        </div>
        <div class="space-y-1 text-xs font-mono">
          <div class="flex justify-between"><span class="text-slate-500">Host:</span> <span class="text-white">{host}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">OS:</span> <span class="text-slate-300 text-[11px]">{os_name}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">ISP:</span> <span class="text-slate-300 text-[11px]">{isp}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Coords:</span> <span class="text-cyan-300">{lat:.4f}, {lon:.4f}</span></div>
        </div>
      </div>

      <!-- Developer CLIs -->
      <div class="space-y-2">
        <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
          <span><i class="fa-solid fa-terminal text-indigo-400"></i> Local CLIs & SDKs</span>
          <span class="text-[10px] text-slate-500 font-mono">{len([c for c in telemetry["clis"] if c["installed"]])}/{len(telemetry["clis"])} Ready</span>
        </div>
        <div class="space-y-1.5">
          {clis_html}
        </div>
      </div>

      <!-- Available Tactical Maps -->
      <div class="space-y-2">
        <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
          <span><i class="fa-solid fa-map-location text-emerald-400"></i> Tactical Maps ({len(telemetry["maps"])})</span>
        </div>
        <div class="space-y-1.5">
          {maps_html}
        </div>
      </div>
    </aside>

    <!-- Map Canvas -->
    <main class="flex-1 relative">
      <div id="map"></div>
    </main>
  </div>

  <script>
    const userLat = {lat};
    const userLon = {lon};
    const hostName = "{host}";
    const pubIP = "{pub_ip}";
    const locIP = "{loc_ip}";

    // Initialize Map with dark carto tiles
    const map = L.map('map').setView([userLat, userLon], 10);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
      attribution: '&copy; CartoDB &copy; OpenStreetMap',
      maxZoom: 19
    }}).addTo(map);

    // Custom Pulse Marker Icon for Local Workstation
    const pulseIcon = L.divIcon({{
      className: 'local-pulse-icon',
      html: '<div class="pulse-ring"></div><div style="width:14px;height:14px;background:#00f0ff;border:2px solid #ffffff;border-radius:50%;position:absolute;left:-7px;top:-7px;box-shadow:0 0 10px #00f0ff;"></div>',
      iconSize: [0, 0]
    }});

    // Add Local Node Marker
    const userMarker = L.marker([userLat, userLon], {{ icon: pulseIcon }}).addTo(map);
    userMarker.bindPopup(`
      <div style="font-family:sans-serif;color:#0f172a;min-width:200px;">
        <h4 style="margin:0;font-size:14px;font-weight:bold;color:#0284c7;">📍 YOU ARE HERE // ${{hostName}}</h4>
        <div style="font-family:monospace;font-size:11px;margin-top:6px;line-height:1.5;">
          <b>Public IP:</b> ${{pubIP}}<br/>
          <b>Local IP:</b> ${{locIP}}<br/>
          <b>Latitude:</b> ${{userLat}}<br/>
          <b>Longitude:</b> ${{userLon}}
        </div>
      </div>
    `).openPopup();

    // Add Investigation Target Node (Huntington Beach Plume & RICO Target)
    const hbLat = 33.6595;
    const hbLon = -117.9988;
    const targetIcon = L.divIcon({{
      className: 'target-pulse-icon',
      html: '<div style="width:12px;height:12px;background:#ef4444;border:2px solid #ffffff;border-radius:50%;position:absolute;left:-6px;top:-6px;box-shadow:0 0 8px #ef4444;"></div>',
      iconSize: [0, 0]
    }});
    const targetMarker = L.marker([hbLat, hbLon], {{ icon: targetIcon }}).addTo(map);
    targetMarker.bindPopup(`
      <div style="font-family:sans-serif;color:#0f172a;min-width:220px;">
        <h4 style="margin:0;font-size:13px;font-weight:bold;color:#dc2626;">🎯 TARGET // HBNC 49x Cr-VI Plume</h4>
        <p style="font-size:11px;margin:4px 0;">17642 Beach Blvd, Huntington Beach, CA</p>
        <a href="/maps/hbnc_rico_gis.html" target="_blank" style="font-size:11px;color:#0284c7;font-weight:bold;">Open Full Plume GIS &rarr;</a>
      </div>
    `);

    // Draw Tactical Connection Vector from Local Node to Target
    const vectorLine = L.polyline([[userLat, userLon], [hbLat, hbLon]], {{
      color: '#00f0ff',
      weight: 2,
      dashArray: '6, 8',
      opacity: 0.7
    }}).addTo(map);

    // Fit map bounds to contain both user and target
    const group = new L.featureGroup([userMarker, targetMarker]);
    map.fitBounds(group.getBounds().pad(0.2));
  </script>
</body>
</html>
"""
