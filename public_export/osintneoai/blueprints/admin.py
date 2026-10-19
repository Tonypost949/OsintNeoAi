from flask import Blueprint
from ._paths import send_rel

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@admin_bp.route('/admin/')
def admin_dashboard():
    return send_rel("admin/master_admin_dashboard.html")
