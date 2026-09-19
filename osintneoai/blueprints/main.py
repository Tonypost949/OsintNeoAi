from flask import Blueprint, send_file
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/signup')
@main_bp.route('/chat')
def public_landing():
    landing_file = r"C:\OsintNeoAi\AG2OSINTNEOMAXX\index.html"
    return send_file(landing_file)
