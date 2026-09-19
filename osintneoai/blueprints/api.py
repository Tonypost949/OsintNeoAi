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
