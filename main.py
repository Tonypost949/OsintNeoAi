"""
OsintNeoAi — Cloud Run entry point.
Exposes API endpoints for OSINT pipeline collection and resolution.
Triggered by Cloud Scheduler or manual HTTP requests.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from flask import Flask, jsonify, request
except ImportError:
    os.system("pip install flask")
    from flask import Flask, jsonify, request

sys.path.insert(0, str(Path(__file__).parent / "osint_pipeline"))

app = Flask(__name__)
START_TIME = datetime.now(timezone.utc)


@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "OsintNeoAi",
        "version": "1.0.0",
        "uptime": str(datetime.now(timezone.utc) - START_TIME),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/collect", methods=["POST"])
def collect():
    """Run OSINT data collection pipeline."""
    from osint_pipeline.watcher import run_pipeline
    try:
        run_pipeline()
        return jsonify({"status": "success", "phase": "collect"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/resolve", methods=["POST"])
def resolve():
    """Run entity resolution pipeline."""
    from osint_pipeline.watcher_v2 import run_phase2
    try:
        run_phase2()
        return jsonify({"status": "success", "phase": "resolve"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/run", methods=["POST"])
def run():
    """Run complete pipeline (collect + resolve)."""
    from osint_pipeline.watcher import run_pipeline
    from osint_pipeline.watcher_v2 import run_phase2
    try:
        run_pipeline()
        run_phase2()
        return jsonify({"status": "success", "phase": "complete"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/export", methods=["GET"])
def export():
    """Export Neo4j batches for download."""
    from osint_pipeline.neo4j_export import get_export_stats
    stats = get_export_stats()
    return jsonify(stats)


@app.route("/results", methods=["GET"])
def list_results():
    """List available result files."""
    results_dir = Path("results")
    if not results_dir.exists():
        return jsonify({"files": []})
    files = [str(f.relative_to(results_dir)) for f in results_dir.glob("**/*") if f.is_file()]
    return jsonify({"files": files})


@app.route("/results/<path:filename>", methods=["GET"])
def get_result(filename):
    """Download a specific result file."""
    filepath = Path("results") / filename
    if not filepath.exists():
        return jsonify({"error": "File not found"}), 404
    return filepath.read_text(encoding="utf-8")


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ── CLI entry point for local testing ─────────────────────────
def cli():
    """Run from command line: python main.py [--mode collect|resolve|complete]"""
    import argparse
    parser = argparse.ArgumentParser(description="OsintNeoAi CLI")
    parser.add_argument("--mode", choices=["collect", "resolve", "complete"], default="collect")
    args = parser.parse_args()

    if args.mode == "collect":
        from osint_pipeline.watcher import run_pipeline
        run_pipeline()
    elif args.mode == "resolve":
        from osint_pipeline.watcher_v2 import run_phase2
        run_phase2()
    elif args.mode == "complete":
        from osint_pipeline.watcher import run_pipeline
        from osint_pipeline.watcher_v2 import run_phase2
        run_pipeline()
        run_phase2()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli()
    else:
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port, debug=False)
