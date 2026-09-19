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

@api_bp.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    return jsonify({
        "status": "SUCCESS",
        "message": "User registered successfully",
        "workspace_id": "usr_workspace_clean_001",
        "redirect_url": "/workspace"
    })

@api_bp.route('/api/auth/session', methods=['GET'])
def api_auth_session():
    return jsonify({
        "authenticated": True,
        "user_type": "public_investigator",
        "workspace_id": "usr_workspace_clean_001",
        "is_blank_workspace": True,
        "personal_data_isolated": True
    })


