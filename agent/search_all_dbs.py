import sqlite3
import os

def check_db(db_name):
    if not os.path.exists(db_name):
        return
    try:
        conn = sqlite3.connect(db_name)
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        for table in tables:
            t = table[0]
            # print(f"Checking table {t} in {db_name}...")
            cols = conn.execute(f"PRAGMA table_info('{t}')").fetchall()
            for col in cols:
                c = col[1]
                if col[2] in ('TEXT', 'VARCHAR'):
                    try:
                        res = conn.execute(f"SELECT * FROM '{t}' WHERE \"{c}\" LIKE '%Guthrie%' OR \"{c}\" LIKE '%Andrew Campos%' OR \"{c}\" LIKE '%Dora Campos%' LIMIT 10").fetchall()
                        if res:
                            print(f"\n--- MATCH IN {db_name} -> {t}.{c} ---")
                            for r in res:
                                print(r)
                    except:
                        pass
    except Exception as e:
        print(f"Error checking {db_name}: {e}")

if __name__ == '__main__':
    dbs = [f for f in os.listdir('.') if f.endswith('.db')]
    print(f"Scanning databases: {dbs}")
    for db in dbs:
        check_db(db)
