from flask import Blueprint, send_file
import os

workspace_bp = Blueprint('workspace', __name__)

@workspace_bp.route('/workspace')
@workspace_bp.route('/workspace/')
@workspace_bp.route('/dev')
def user_workspace():
    dev_file = r"C:\OsintNeoAi\web\index.html"
    return send_file(dev_file)
