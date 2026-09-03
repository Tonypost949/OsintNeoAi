import os
import re
from pathlib import Path

files_to_fix = [
    Path(r'C:\OsintNeoAi\gods_eye_view.html'),
    Path(r'C:\OsintNeoAi\public\gods_eye_view.html'),
    Path(r'C:\OsintNeoAi\docs\gods_eye_view.html'),
    Path(r'C:\OsintNeoAi\data_apps\gods_eye_view.html')
]

print("=== FIXING BROKEN LINKS & ASSETS IN GODS EYE VIEW DASHBOARD ===")

for p in files_to_fix:
    if p.exists():
        content = p.read_text(encoding='utf-8', errors='ignore')
        
        # 1. Replace local non-existent cesium paths with reliable CesiumJS CDN
        content_fixed = re.sub(
            r'<script src="/cesium/Cesium\.js"></script>',
            '<script src="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Cesium.js"></script>',
            content
        )
        content_fixed = re.sub(
            r'<link rel="stylesheet" href="/cesium/Widgets/widgets\.css">',
            '<link rel="stylesheet" href="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Widgets/widgets.css">',
            content_fixed
        )
        
        # 2. Fix relative assets paths to work seamlessly both locally and hosted on Azure / GitHub Pages
        content_fixed = content_fixed.replace('href="/nav-polish.css"', 'href="nav-polish.css"')
        content_fixed = content_fixed.replace('href="/public/nav-polish.css"', 'href="nav-polish.css"')
        
        p.write_text(content_fixed, encoding='utf-8')
        print(f"✓ Fixed broken links in: {p}")
    else:
        print(f"[-] File missing: {p}")
