import sqlite3
import shutil
import os
import glob

def check_chrome():
    chrome_history = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History")
    tmp_history = r"C:\OsintNeoAi\data\chrome_history_tmp.db"

    # Also search across all profile directories in User Data
    user_data = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")
    history_files = glob.glob(os.path.join(user_data, "*", "History")) + [chrome_history]

    for h_path in set(history_files):
        if os.path.exists(h_path) and not os.path.isdir(h_path):
            print(f"\n==========================================")
            print(f"Checking Profile History: {h_path}")
            print(f"==========================================")
            try:
                shutil.copy2(h_path, tmp_history)
                conn = sqlite3.connect(tmp_history)
                cursor = conn.cursor()

                print("--- RECENT DOWNLOADS ---")
                try:
                    cursor.execute("SELECT target_path, tab_url, start_time, total_bytes FROM downloads ORDER BY start_time DESC LIMIT 15")
                    for row in cursor.fetchall():
                        print(f"File: {row[0]} | URL: {row[1][:80]} | Bytes: {row[3]}")
                except Exception as e:
                    print("Downloads query error:", e)

                print("\n--- RECENT TAKEOUT / GOOGLE DOWNLOAD URLS ---")
                try:
                    cursor.execute("SELECT url, title, last_visit_time FROM urls WHERE url LIKE '%takeout%' OR url LIKE '%googleusercontent%' ORDER BY last_visit_time DESC LIMIT 15")
                    for row in cursor.fetchall():
                        print(f"Title: {row[1]} | URL: {row[0]}")
                except Exception as e:
                    print("URLs query error:", e)

                conn.close()
                if os.path.exists(tmp_history):
                    os.remove(tmp_history)
            except Exception as e:
                print(f"Error accessing {h_path}: {e}")

if __name__ == "__main__":
    check_chrome()
