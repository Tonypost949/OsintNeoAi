from flask import Blueprint
from ._paths import send_rel

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/signup')
@main_bp.route('/landing')
def public_landing():
    return send_rel("core/AG2OSINTNEOMAXX/public_landing.html")

