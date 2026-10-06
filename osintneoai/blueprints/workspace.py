from flask import Blueprint
from ._paths import send_rel

workspace_bp = Blueprint('workspace', __name__)

@workspace_bp.route('/workspace')
@workspace_bp.route('/workspace/')
@workspace_bp.route('/chat')
def user_workspace():
    return send_rel("public/workspace_chat.html")

@workspace_bp.route('/dev')
@workspace_bp.route('/dev/')
def dev_workspace():
    return send_rel("web/index.html")

@workspace_bp.route('/legal')
@workspace_bp.route('/legal/')
def legal_portal():
    return send_rel("workspace/whistleblower_legal_index.html")

@workspace_bp.route('/legal/omnichannel')
def legal_omnichannel():
    return send_rel("workspace/omnichannel_legal_hub.html")

@workspace_bp.route('/legal/conflicts')
def legal_conflicts():
    return send_rel("workspace/legal_conflict_audit_dossier.html")

@workspace_bp.route('/status')
@workspace_bp.route('/dashboard/status')
def system_status():
    return send_rel("workspace/system_status_widget.html")


