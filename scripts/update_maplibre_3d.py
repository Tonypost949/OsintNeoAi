import json
import os
import shutil
from datetime import datetime

def update_3d_tactical_dashboard():
    html_path = r"C:\OsintNeoAi\maplibre_3d_tactical.html"
    web_dir_repo = r"C:\OsintNeoAi\web"
    web_dir_v1 = r"C:\Amd949609_Antigravity_v1\web"

    os.makedirs(web_dir_repo, exist_ok=True)
    os.makedirs(web_dir_v1, exist_ok=True)

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    ma_nodes_code = """
    // 4. MASSACHUSETTS COUNTERFEIT PILL 3D TIMELINE NODES
    add3DMarker([-70.9180, 42.5200], '💊 North Shore Bust Node (2020-04-12)', 'Location: North Shore, MA • Event: Initial counterfeit pill distribution network flagged');
    add3DMarker([-70.6720, 42.0410], '📍 Duxbury Interdiction Node (2021-08-19)', 'Location: Duxbury, MA • Event: Interdiction of illicit pill press operation');
    add3DMarker([-70.6670, 41.9580], '📍 Plymouth Surveillance Nexus (2023-01-15)', 'Location: Plymouth, MA • Event: Cross-county distribution surveillance');
    add3DMarker([-70.9380, 42.0810], '🚨 Whitman Lab Raid Node (2023-11-04)', 'Location: Whitman, MA • Event: State police raid on active pill manufacturing lab');
    add3DMarker([-71.0589, 42.3601], '🏛️ Boston Federal Indictment Node (2024-02-28)', 'Location: Boston, MA • Event: Federal grand jury indictment returned');

    // 5. NEURAL OCR EVIDENCE LOCKER RECORDS
    add3DMarker([-71.0500, 42.3500], '📑 Court Photo Record 1 (Sewer Service Fraud)', 'Doc ID: court_photo_1 • Account: amd949609@gmail.com • Category: COURT_PLEADING_AFFIDAVIT');
    add3DMarker([-71.0600, 42.3550], '📑 Court Photo Record 2 (Default Judgment Notice)', 'Doc ID: court_photo_2 • Account: anthonymichaeldimarcello@gmail.com • Category: DEFAULT_JUDGMENT_NOTICE');
    add3DMarker([-71.0700, 42.3600], '📑 Eviction Photo Record 2 (Constable Return Fraud)', 'Doc ID: eviction_photo_2 • Account: anthonymichaeldimarcello@gmail.com • Finding: Sewer Service Fraud EXIF timestamp mismatch');
"""

    if "MASSACHUSETTS COUNTERFEIT PILL 3D TIMELINE NODES" not in html_content:
        html_content = html_content.replace(
            "add3DMarker([-114.9200, 36.3150], '🏜️ Apex Desert Industrial Mesh', '36.3150° N, 114.9200° W • Clark County');",
            "add3DMarker([-114.9200, 36.3150], '🏜️ Apex Desert Industrial Mesh', '36.3150° N, 114.9200° W • Clark County');\n" + ma_nodes_code
        )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Copy to web/index.html in repo & v1
    web_index_repo = os.path.join(web_dir_repo, "index.html")
    web_index_v1 = os.path.join(web_dir_v1, "index.html")

    shutil.copy2(html_path, web_index_repo)
    shutil.copy2(html_path, web_index_v1)

    print(f"Updated 3D WebGL Dashboard and deployed to:\n- {web_index_repo}\n- {web_index_v1}")

if __name__ == "__main__":
    update_3d_tactical_dashboard()
