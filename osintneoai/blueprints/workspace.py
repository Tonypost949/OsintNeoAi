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

