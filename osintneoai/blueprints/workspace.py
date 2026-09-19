from flask import Blueprint, send_file
import os

workspace_bp = Blueprint('workspace', __name__)

@workspace_bp.route('/workspace')
@workspace_bp.route('/workspace/')
@workspace_bp.route('/chat')
def user_workspace():
    workspace_file = r"C:\OsintNeoAi\public\workspace_chat.html"
    return send_file(workspace_file)

@workspace_bp.route('/dev')
@workspace_bp.route('/dev/')
def dev_workspace():
    dev_file = r"C:\OsintNeoAi\web\index.html"
    return send_file(dev_file)

@workspace_bp.route('/legal')
@workspace_bp.route('/legal/')
def legal_portal():
    legal_file = r"C:\OsintNeoAi\workspace\whistleblower_legal_index.html"
    return send_file(legal_file)

@workspace_bp.route('/legal/omnichannel')
def legal_omnichannel():
    legal_file = r"C:\OsintNeoAi\workspace\omnichannel_legal_hub.html"
    return send_file(legal_file)

@workspace_bp.route('/legal/conflicts')
def legal_conflicts():
    legal_file = r"C:\OsintNeoAi\workspace\legal_conflict_audit_dossier.html"
    return send_file(legal_file)


