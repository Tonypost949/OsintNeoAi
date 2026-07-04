#!/usr/bin/env python3
"""Prepare notebooks for Colab compatibility"""

import json
import sys
from pathlib import Path

def prepare_for_colab(notebook_path):
    """Add Colab-specific cells to notebook"""
    
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    # Colab setup cell
    colab_setup = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"colab": {"base_uri": "https://localhost:8080/"}, "id": "setup"},
        "outputs": [],
        "source": [
            "# Google Colab Setup\n",
            "import os\n",
            "from google.colab import userdata\n",
            "from google.colab import drive\n",
            "\n",
            "# Mount Google Drive\n",
            "drive.mount('/content/drive')\n",
            "\n",
            "# Get API key from Colab secrets\n",
            "GEMINI_API_KEY = userdata.get('GEMINI_API_KEY')\n",
            "os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY\n",
            "\n",
            "# Clone repo if not already present\n",
            "import subprocess\n",
            "result = subprocess.run(['git', 'status'], capture_output=True)\n",
            "if result.returncode != 0:\n",
            "    !git clone https://github.com/Tonypost949/OsintNeoAi.git\n",
            "    %cd OsintNeoAi\n",
            "\n",
            "# Install dependencies\n",
            "!pip install -q -r requirements.txt\n",
            "\n",
            "print('✅ Colab setup complete!')\n"
        ]
    }
    
    # Insert setup cell at beginning
    nb['cells'].insert(0, colab_setup)
    
    # Add Git integration cell at end
    git_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"id": "git_sync"},
        "outputs": [],
        "source": [
            "# Sync results back to GitHub\n",
            "import subprocess\n",
            "from datetime import datetime\n",
            "\n",
            "subprocess.run(['git', 'config', 'user.name', 'Colab Bot'])\n",
            "subprocess.run(['git', 'config', 'user.email', 'colab@research.google.com'])\n",
            "subprocess.run(['git', 'add', '-A'])\n",
            "subprocess.run(['git', 'commit', '-m', f'Results from Colab - {datetime.utcnow().isoformat()}'])\n",
            "subprocess.run(['git', 'push'])\n",
            "print('✅ Results synced to GitHub')\n"
        ]
    }
    
    nb['cells'].append(git_cell)
    
    # Save modified notebook
    with open(notebook_path, 'w') as f:
        json.dump(nb, f, indent=2)
    
    print(f"✅ Prepared {notebook_path} for Colab")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python prepare_colab.py <notebook_path>")
        sys.exit(1)
    
    prepare_for_colab(sys.argv[1])
