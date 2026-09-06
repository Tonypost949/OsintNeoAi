import os
import sys

# Import full OSINTNeoAiCLI_v2 master Flask app for Azure App Service
from OSINTNeoAiCLI_v2 import app as app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
