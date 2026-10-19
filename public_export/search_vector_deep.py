import sqlite3
import json

def query_vector_db_deep():
    db_path = r"C:\OsintNeoAi\osint_vector_index.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM osint_nodes;")
    rows = cur.fetchall()
    
    categories = ['chase', 'tmobile', 't-mobile', 'identity', 'insurance', 'mercy', 'bank', 'fraud']
    results = {k: [] for k in categories}
    
    for r in rows:
        r_str = str(r).lower()
        for k in categories:
            if k in r_str:
                results[k].append(r)
                
    summary = {k: len(results[k]) for k in results}
    print("[+] Vector Database Search Results:")
    print(json.dumps(summary, indent=2))
    conn.close()

if __name__ == "__main__":
    query_vector_db_deep()
