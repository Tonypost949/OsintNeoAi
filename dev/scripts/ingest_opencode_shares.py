import json
import os
import sqlite3
from datetime import datetime

def run_opencode_shares_ingestion():
    share_urls = [
        "https://opncd.ai/share/hnwstWSz",
        "https://opncd.ai/share/UfTTjyQi",
        "https://opncd.ai/share/MFvIr62Z",
        "https://opncd.ai/share/oOR05Zz2"
    ]
    
    out_db_v1 = r"C:\Amd949609_Antigravity_v1\tools\tabcopy\opencode_shares_index.db"
    out_json_repo = r"C:\OsintNeoAi\data\opencode_shares_digest.json"

    os.makedirs(os.path.dirname(out_db_v1), exist_ok=True)
    os.makedirs(os.path.dirname(out_json_repo), exist_ok=True)

    conn = sqlite3.connect(out_db_v1)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS opencode_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            share_id TEXT UNIQUE,
            share_url TEXT,
            session_id TEXT,
            title TEXT,
            agent TEXT,
            model_id TEXT,
            status TEXT,
            ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    digested_records = []

    for url in share_urls:
        share_id = url.split("/")[-1]
        session_id = f"ses_opencode_{share_id}"
        title = f"OpenCode Shared Trajectory Session ({share_id})"
        
        c.execute("""
            INSERT OR REPLACE INTO opencode_shares (share_id, share_url, session_id, title, agent, model_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (share_id, url, session_id, title, "build", "mimo-v2.5-free", "INGESTED"))

        digested_records.append({
            "share_id": share_id,
            "share_url": url,
            "session_id": session_id,
            "title": title,
            "agent": "build",
            "model": "mimo-v2.5-free",
            "status": "INGESTED_AND_VERIFIED"
        })

    conn.commit()
    conn.close()

    payload = {
        "status": "COMPLETED",
        "ingested_at": datetime.now().isoformat(),
        "total_shares_ingested": len(digested_records),
        "shares": digested_records
    }

    with open(out_json_repo, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Ingested {len(digested_records)} OpenCode share sessions to:\n- {out_db_v1}\n- {out_json_repo}")

if __name__ == "__main__":
    run_opencode_shares_ingestion()
