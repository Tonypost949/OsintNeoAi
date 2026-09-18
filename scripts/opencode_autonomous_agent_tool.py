# OpenCode Extracted Autonomous AI Tool
# Generated At: 2026-09-18
import os
import sys
import json
import sqlite3

def run_opencode_autonomous_agent_tool():
    print("Executing OpenCode Shared Trajectory Autonomous Tool...")
    db_path = r"C:\Amd949609_Antigravity_v1\tools\tabcopy\opencode_shares_index.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT share_id, share_url, session_id, title, status FROM opencode_shares")
        rows = c.fetchall()
        conn.close()
        print(f"Verified {len(rows)} registered OpenCode AI sessions in local database.")
        for row in rows:
            print(f"- Session {row[0]}: {row[3]} [{row[4]}]")
    else:
        print("Database not found.")

if __name__ == "__main__":
    run_opencode_autonomous_agent_tool()
