#!/usr/bin/env python3
"""Generate direct links to Colab notebooks"""

from pathlib import Path
import sys

def generate_colab_links():
    """Generate markdown with Colab notebook links"""
    
    notebooks = list(Path('.').glob('**/*.ipynb'))
    notebooks = [nb for nb in notebooks if '.github' not in str(nb)]
    
    if not notebooks:
        print("No notebooks found")
        return
    
    print("# 📓 Colab Notebooks\n")
    print("Open these notebooks directly in Google Colab:\n")
    
    for notebook in sorted(notebooks):
        # Create GitHub raw URL
        raw_url = f"https://raw.githubusercontent.com/Tonypost949/OsintNeoAi/main/{notebook}"
        
        # Create Colab URL
        colab_url = f"https://colab.research.google.com/github/Tonypost949/OsintNeoAi/blob/main/{notebook}"
        
        # Extract notebook name
        name = notebook.stem
        
        print(f"- **{name}**: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)]({colab_url})")
    
    print("\n## How to Use\n")
    print("1. Click the 'Open in Colab' button")
    print("2. Go to Secrets (🔑 icon) and add `GEMINI_API_KEY`")
    print("3. Run the notebook cells")
    print("4. Results auto-sync back to GitHub\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(generate_colab_links())
