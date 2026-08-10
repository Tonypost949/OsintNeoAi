import os
import sys
from flask import Flask, jsonify, send_from_directory, render_template_string

# Import API app from api.main
from api.main import app as api_app

app = api_app

@app.route("/", methods=["GET"])
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
            "arcgis_geojson": "/arcgis/geojson"
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
