import os
from flask import Flask, send_from_directory, abort
from osintneoai.blueprints import main_bp, admin_bp, workspace_bp, api_bp

def create_app():
    app = Flask(__name__, static_folder='.')
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(workspace_bp)
    app.register_blueprint(api_bp)

    # Static file fallback
    @app.route('/<path:filename>')
    def serve_static_file(filename):
        search_dirs = [
            ROOT_DIR,
            os.path.join(ROOT_DIR, 'public'),
            os.path.join(ROOT_DIR, 'workspace'),
            os.path.join(ROOT_DIR, 'admin'),
            os.path.join(ROOT_DIR, 'dev'),
            os.path.join(ROOT_DIR, 'docs'),
            os.path.join(ROOT_DIR, 'opencode_work'),
            os.path.join(ROOT_DIR, 'data_apps'),
        ]
        for dir_path in search_dirs:
            p = os.path.join(dir_path, filename)
            if os.path.exists(p) and os.path.isfile(p):
                return send_from_directory(dir_path, filename)
        abort(404)

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
