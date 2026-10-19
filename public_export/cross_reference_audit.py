import os
import json
import sqlite3
import csv

def run_cross_reference():
    results = {}

    # 1. Check local SQLite Vector Index
    db_path = r"C:\OsintNeoAi\osint_vector_index.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        results["sqlite_tables"] = tables
        if "vector_nodes" in tables or "nodes" in tables:
            tbl = "vector_nodes" if "vector_nodes" in tables else "nodes"
            cur.execute(f"SELECT COUNT(*) FROM {tbl};")
            results["sqlite_vector_count"] = cur.fetchone()[0]
        conn.close()
    else:
        results["sqlite_tables"] = []

    # 2. Check Master CSV Node Database
    csv_path = r"C:\Amd949609_Antigravity_v1\user_nodes.csv"
    if os.path.exists(csv_path):
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            results["master_csv_nodes"] = len(rows)
    else:
        results["master_csv_nodes"] = 0

    # 3. Check Physical Evidence Locker SHA256 Manifest
    manifest_path = r"C:\OsintNeoAi\EVIDENCE_LOCKER_SHA256_MANIFEST.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                results["evidence_locker_files"] = len(data)
            elif isinstance(data, dict):
                results["evidence_locker_files"] = len(data.get("files", data.get("manifest", [])))
    else:
        results["evidence_locker_files"] = 0

    # 4. Check Academic Database Menu items
    menu_path = r"C:\OsintNeoAi\Database Menu.html"
    if os.path.exists(menu_path):
        with open(menu_path, mode="r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            results["oclc_proxy_links"] = content.count("americansentinel.idm.oclc.org/login")
    else:
        results["oclc_proxy_links"] = 0

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_cross_reference()
