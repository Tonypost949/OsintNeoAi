from flask import Blueprint, send_file
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/signup')
@main_bp.route('/landing')
def public_landing():
    landing_file = r"C:\OsintNeoAi\core\AG2OSINTNEOMAXX\public_landing.html"
    return send_file(landing_file)

