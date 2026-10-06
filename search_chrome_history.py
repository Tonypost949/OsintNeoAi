import sqlite3
import os
import glob
import shutil

def search_chrome_history():
    pattern = r"C:\Users\Amd949609\AppData\Local\Google\Chrome\User Data\*\History"
    history_files = glob.glob(pattern)
    history_files.append(r"C:\Users\Amd949609\AppData\Local\Google\Chrome\User Data\Default\History")
    
    keywords = ["Shea", "Roundtree", "Anaheim", "Stadium", "Sidhu", "K5", "K-5"]
    
    for hf in set(history_files):
        if not os.path.isfile(hf):
            continue
        tmp_db = hf + ".tmp_scan"
        try:
            shutil.copy2(hf, tmp_db)
            conn = sqlite3.connect(tmp_db)
            cursor = conn.cursor()
            
            for kw in keywords:
                query = f"SELECT url, title, last_visit_time FROM urls WHERE title LIKE '%{kw}%' OR url LIKE '%{kw}%'"
                cursor.execute(query)
                rows = cursor.fetchall()
                if rows:
                    print(f"=== Matches for '{kw}' in {hf} ===")
                    for r in rows[:10]:
                        print(f"URL: {r[0]} | Title: {r[1]}")
            
            conn.close()
            os.remove(tmp_db)
        except Exception as e:
            if os.path.exists(tmp_db):
                try: os.remove(tmp_db)
                except: pass

if __name__ == "__main__":
    search_chrome_history()
