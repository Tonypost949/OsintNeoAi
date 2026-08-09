import sqlite3

def check_db(db_name):
    print(f"--- Checking {db_name} ---")
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        
        # Check tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        
        for table in tables:
            t = table[0]
            try:
                # search for keywords in all text columns
                cur.execute(f"PRAGMA table_info({t})")
                cols = [c[1] for c in cur.fetchall() if c[2] in ('TEXT', 'VARCHAR')]
                for col in cols:
                    cur.execute(f"SELECT {col} FROM {t} WHERE LOWER({col}) LIKE '%immigrant%' OR LOWER({col}) LIKE '%migrant%' OR LOWER({col}) LIKE '%unaccompanied%' LIMIT 5")
                    res = cur.fetchall()
                    if res:
                        print(f"Found in {t}.{col}: {res}")
            except Exception as e:
                pass
    except Exception as e:
        print(f"Failed to check {db_name}: {e}")

check_db('master_index.db')
check_db('master_index_v2.db')
check_db('cases.db')
