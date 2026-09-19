import sqlite3
import shutil
import os
import glob

tmp_history = r"C:\OsintNeoAi\data\chrome_history_tmp.db"
user_data = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")
history_files = glob.glob(os.path.join(user_data, "*", "History"))

for h_path in history_files:
    if os.path.exists(h_path) and not os.path.isdir(h_path):
        try:
            shutil.copy2(h_path, tmp_history)
            conn = sqlite3.connect(tmp_history)
            cursor = conn.cursor()
            query = "SELECT url, title, last_visit_time FROM urls WHERE url LIKE '%takeout%' OR title LIKE '%Takeout%' ORDER BY last_visit_time DESC LIMIT 5"
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                print(f"=== Matches in {os.path.basename(os.path.dirname(h_path))} ===")
                for r in rows:
                    print(f"  {r[1]} --> {r[0]}")
            conn.close()
            if os.path.exists(tmp_history):
                os.remove(tmp_history)
        except Exception as e:
            pass
