from flask import Flask, send_from_directory, send_file
import os

app = Flask(__name__)
BASE = r"C:\OsintNeoAi"

# Serve hub at root
@app.route("/")
def hub():
    return send_file(os.path.join(BASE, "maps_hub.html"))

@app.route("/maps_hub.html")
def hub2():
    return send_file(os.path.join(BASE, "maps_hub.html"))

# Serve maps from multiple locations
MAP_DIRS = [
    BASE,
    os.path.join(BASE, "docs"),
    os.path.join(BASE, "opencode_work"),
    os.path.join(BASE, "evidence", "visualizations"),
    os.path.join(BASE, "workspaces", "osint-agent"),
]

@app.route("/maps/<path:filename>")
def serve_map(filename):
    for d in MAP_DIRS:
        fp = os.path.join(d, filename)
        if os.path.exists(fp):
            return send_file(fp)
    return f"Map {filename} not found", 404

@app.route("/map/<path:filename>")
def serve_map2(filename):
    return serve_map(filename)

# Compatibility: /map/master -> hub
@app.route("/map/master")
def master():
    return send_file(os.path.join(BASE, "maps_hub.html"))

@app.route("/<path:filename>")
def fallback(filename):
    fp = os.path.join(BASE, filename)
    if os.path.exists(fp) and os.path.isfile(fp):
        return send_file(fp)
    return f"Not found: {filename}", 404

if __name__ == "__main__":
    print("Maps Hub serving at http://localhost:10000/")
    print("Hub: http://localhost:10000/")
    print("Master alias: http://localhost:10000/map/master")
    app.run(host="0.0.0.0", port=10000, debug=False)
