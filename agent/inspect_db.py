import sqlite3

def inspect_db(db_name):
    print(f"\n===== Inspecting {db_name} =====")
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            t_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM `{t_name}`")
            count = cursor.fetchone()[0]
            print(f"Table: {t_name} | Rows: {count}")
    except Exception as e:
        print(f"Error reading {db_name}: {e}")

inspect_db("master_index.db")
inspect_db("master_index_v2.db")
