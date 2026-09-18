import json
import os
import sqlite3
from datetime import datetime

def extract_and_register_opencode_tools():
    digest_path = r"C:\OsintNeoAi\data\opencode_shares_digest.json"
    tools_dir_v1 = r"C:\Amd949609_Antigravity_v1\tools"
    tools_dir_repo = r"C:\OsintNeoAi\scripts"

    os.makedirs(tools_dir_v1, exist_ok=True)
    os.makedirs(tools_dir_repo, exist_ok=True)

    tool_script_content = '''# OpenCode Extracted Autonomous AI Tool
# Generated At: 2026-09-18
import os
import sys
import json
import sqlite3

def run_opencode_autonomous_agent_tool():
    print("Executing OpenCode Shared Trajectory Autonomous Tool...")
    db_path = r"C:\\Amd949609_Antigravity_v1\\tools\\tabcopy\\opencode_shares_index.db"
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
'''

    tool_file_v1 = os.path.join(tools_dir_v1, "opencode_autonomous_agent_tool.py")
    tool_file_repo = os.path.join(tools_dir_repo, "opencode_autonomous_agent_tool.py")

    with open(tool_file_v1, "w", encoding="utf-8") as f:
        f.write(tool_script_content)

    with open(tool_file_repo, "w", encoding="utf-8") as f:
        f.write(tool_script_content)

    print(f"Extracted and registered OpenCode AI tool to:\n- {tool_file_v1}\n- {tool_file_repo}")

if __name__ == "__main__":
    extract_and_register_opencode_tools()
