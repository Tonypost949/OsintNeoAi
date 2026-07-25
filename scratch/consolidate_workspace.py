import os
import shutil

root_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi"

# 1. Target Directories
dirs_to_create = [
    r"core\connectors",
    r"core\graph",
    r"core\analysis",
    r"cli",
    r"database\queries",
    r"pipelines\ingestion",
    r"pipelines\backups",
    r"archive"
]

print("=== Creating directories ===")
for d in dirs_to_create:
    p = os.path.join(root_dir, d)
    if not os.path.exists(p):
        os.makedirs(p)
        print(f"Created: {p}")

# Helper function to move file if exists
def move_file(src, dest):
    src_path = os.path.join(root_dir, src)
    dest_path = os.path.join(root_dir, dest)
    if os.path.exists(src_path):
        try:
            # If target exists and is a file, remove it first
            if os.path.exists(dest_path) and os.path.isfile(dest_path):
                os.remove(dest_path)
            shutil.move(src_path, dest_path)
            print(f"Moved: {src} -> {dest}")
        except Exception as e:
            print(f"Error moving {src}: {e}")

# Helper function to move folder if exists
def move_folder(src, dest):
    src_path = os.path.join(root_dir, src)
    dest_path = os.path.join(root_dir, dest)
    if os.path.exists(src_path) and os.path.isdir(src_path):
        try:
            if os.path.exists(dest_path):
                # If destination already exists, copy tree files and remove source
                for r, ds, fs in os.walk(src_path):
                    for f in fs:
                        sp = os.path.join(r, f)
                        rel = os.path.relpath(sp, src_path)
                        dp = os.path.join(dest_path, rel)
                        os.makedirs(os.path.dirname(dp), exist_ok=True)
                        shutil.copy2(sp, dp)
                shutil.rmtree(src_path)
            else:
                shutil.move(src_path, dest_path)
            print(f"Moved directory: {src} -> {dest}")
        except Exception as e:
            print(f"Error moving folder {src}: {e}")

print("\n=== Consolidating root files ===")
# DDLs and SQL Queries
move_file("address_cluster_monitor.sql", r"database\queries\address_cluster_monitor.sql")
move_file("cross_jurisdiction_funnel.sql", r"database\queries\cross_jurisdiction_funnel.sql")
move_file("hub_degree_anomaly.sql", r"database\queries\hub_degree_anomaly.sql")

# Analysis & Core Backend
move_file("anomaly_alerts.py", r"core\analysis\anomaly_alerts.py")
move_file("business_workbook_engine.py", r"core\analysis\business_workbook_engine.py")
move_file("extract_chokepoints.py", r"core\analysis\extract_chokepoints.py")
move_file("osint_dashboard.py", r"core\analysis\osint_dashboard.py")
move_file("osint_db.py", r"core\analysis\osint_db.py")
move_file("osint_workbook_engine.py", r"core\analysis\osint_workbook_engine.py")
move_file("osint_utils.py", r"core\analysis\osint_utils.py")

# Ingestion / Pipelines
move_file("setup_kb.py", r"pipelines\ingestion\setup_kb.py")
move_file("osint_setup.py", r"pipelines\ingestion\osint_setup.py")
move_file("osint_repo_aggregator.py", r"pipelines\ingestion\osint_repo_aggregator.py")

# Archive legacy zip extraction subfolders
legacy_repos = [
    "OSINTNeoAiCLI",
    "OSINTNeoAiXL",
    "OsintNeoAi52026",
    "OsintNeoAiXXXL",
    "osint-agent",
    "osint_analyzer",
    "riconow"
]

print("\n=== Archiving legacy zip folders ===")
for r in legacy_repos:
    move_folder(r, os.path.join("archive", r))

print("\n=== Consolidation flow complete ===")
