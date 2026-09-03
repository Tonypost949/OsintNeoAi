import os
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='.')

@app.route('/')
def root():
    if os.path.exists('gods_eye_view_live.html'):
        return send_from_directory('.', 'gods_eye_view_live.html')
    return send_from_directory('.', 'hbnc_rico_gis.html')

@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
