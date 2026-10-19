"""
Root WSGI Entrypoint for Azure App Service
"""
from api.app import app

if __name__ == "__main__":
    app.run()
