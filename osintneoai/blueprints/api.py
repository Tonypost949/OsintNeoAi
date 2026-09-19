from flask import Blueprint, jsonify
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/status')
def api_status():
    return jsonify({
        "status": "HEALTHY",
        "version": "1.0.0",
        "service": "OSINTNeoAI Blueprints Engine"
    })

@api_bp.route('/api/legal/workspace-data')
def api_legal_workspace_data():
    return jsonify({
        "connected_workspace": r"C:\OsintNeoAi\workspace",
        "cloud_database_status": {
            "bigquery_dataset": "noble-beanbag-497411-m4",
            "edr_hits": 10116,
            "spanner_instance": "brainmedus-spanner",
            "spanner_database": "osint_graph_db",
            "crossref_apns": 15
        },
        "legal_modules": [
            {"name": "Whistleblower Reward Library", "route": "/legal"},
            {"name": "Omni-Channel Legal Dispatch", "route": "/legal/omnichannel"},
            {"name": "Statutory & Conflict Audit Dossier", "route": "/legal/conflicts"}
        ]
    })

