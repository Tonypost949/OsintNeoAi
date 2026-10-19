from flask import Blueprint, send_file
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@admin_bp.route('/admin/')
def admin_dashboard():
    admin_file = r"C:\OsintNeoAi\admin\master_admin_dashboard.html"
    return send_file(admin_file)
