import os
import sys
from flask import Flask, jsonify, send_from_directory, render_template_string

# Import API app from api.main
from api.main_v2 import app as api_app

app = api_app

@app.route("/api", methods=["GET"])
def home():
    """Root route returning service health and API map."""
    return jsonify({
        "status": "online",
        "service": "OSINT Neo AI Cloud Engine",
        "version": "3.0.0",
        "endpoints": {
            "status": "/api/status",
            "bookmarks": "/api/bookmarks/list",
            "pipeline_run": "/api/pipeline/run",
            "pipeline_resolve": "/api/pipeline/resolve",
            "arcgis_dashboard": "/arcgis",
            "arcgis_geojson": "/arcgis/geojson",
            "maps": {
                "master_tactical": "/map/master",
                "badass_osint": "/map/badass",
                "hbnc_rico": "/map/hbnc",
                "nationwide_coc": "/map/coc",
                "nationwide_pipeline": "/map/pipeline",
                "comparison_swipe": "/map/comparison"
            }
        }
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/arcgis", methods=["GET"])
def arcgis_dashboard():
    dashboard_path = os.path.join(os.path.dirname(__file__), "arcgis_teams_dashboard.html")
    if os.path.exists(dashboard_path):
        with open(dashboard_path, "r", encoding="utf-8") as f:
            return render_template_string(f.read())
    return jsonify({"error": "Dashboard not found"}), 404

@app.route("/arcgis/geojson", methods=["GET"])
def arcgis_geojson():
    geojson_path = os.path.join(os.path.dirname(__file__), "arcgis_for_teams_geojson.geojson")
    if os.path.exists(geojson_path):
        return send_from_directory(os.path.dirname(__file__), "arcgis_for_teams_geojson.geojson", mimetype="application/geo+json")
    return jsonify({"error": "GeoJSON not found"}), 404

# Tactical GIS Maps with Multiple Route Aliases
@app.route("/map/master", methods=["GET"])
@app.route("/maps/master_tactical_gis.html", methods=["GET"])
def master_tactical_map():
    map_file = os.path.join(os.path.dirname(__file__), "master_tactical_gis.html")
    if os.path.exists(map_file):
        with open(map_file, "r", encoding="utf-8") as f:
            return render_template_string(f.read())
    return jsonify({"error": "Master tactical map not found"}), 404

@app.route("/map/badass", methods=["GET"])
@app.route("/maps/badass_osint_map.html", methods=["GET"])
def badass_osint_map():
    map_file = os.path.join(os.path.dirname(__file__), "badass_osint_map.html")
    if os.path.exists(map_file):
        with open(map_file, "r", encoding="utf-8") as f:
            return render_template_string(f.read())
    return jsonify({"error": "Badass OSINT map not found"}), 404

@app.route("/map/hbnc", methods=["GET"])
@app.route("/maps/hbnc_rico_gis.html", methods=["GET"])
def hbnc_rico_map():
    map_file = os.path.join(os.path.dirname(__file__), "hbnc_rico_gis.html")
    if os.path.exists(map_file):
        with open(map_file, "r", encoding="utf-8") as f:
            return render_template_string(f.read())
    return jsonify({"error": "HBNC RICO map not found"}), 404

@app.route("/map/coc", methods=["GET"])
@app.route("/maps/nationwide_coc_map.html", methods=["GET"])
def nationwide_coc_map():
    map_file = os.path.join(os.path.dirname(__file__), "nationwide_coc_map.html")
    if os.path.exists(map_file):
        with open(map_file, "r", encoding="utf-8") as f:
            return render_template_string(f.read())
    return jsonify({"error": "Chain of custody map not found"}), 404

@app.route("/map/pipeline", methods=["GET"])
@app.route("/maps/nationwide_pipeline_map.html", methods=["GET"])
def nationwide_pipeline_map():
    map_file = os.path.join(os.path.dirname(__file__), "nationwide_pipeline_map.html")
    if os.path.exists(map_file):
        with open(map_file, "r", encoding="utf-8") as f:
            return render_template_string(f.read())
    return jsonify({"error": "Pipeline map not found"}), 404

@app.route("/map/comparison", methods=["GET"])
@app.route("/maps/comparison_swipe_map.html", methods=["GET"])
def comparison_swipe_map():
    map_file = os.path.join(os.path.dirname(__file__), "comparison_swipe_map.html")
    if os.path.exists(map_file):
        with open(map_file, "r", encoding="utf-8") as f:
            return render_template_string(f.read())
    return jsonify({"error": "Comparison map not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
