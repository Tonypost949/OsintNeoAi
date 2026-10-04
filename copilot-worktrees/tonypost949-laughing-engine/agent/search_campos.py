import sqlite3

def search_db(db_name, query, params=()):
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute(query, params)
        res = cur.fetchall()
        print(f"--- Results from {db_name} ---")
        if not res:
            print("No matches.")
        for r in res:
            print(r)
    except Exception as e:
        print(f"Error reading {db_name}: {e}")

if __name__ == '__main__':
    # Search cases.db
    q1 = "SELECT id, title, description FROM cases WHERE description LIKE '%Guthrie%' OR description LIKE '%Andrew Campos%' OR description LIKE '%Dora Campos%'"
    search_db('cases.db', q1)
    
    # Search master_index.db if it exists, maybe checking the text table
    q2 = "SELECT id, file_path, extracted_text FROM documents WHERE extracted_text LIKE '%Guthrie%' OR extracted_text LIKE '%Andrew Campos%' OR extracted_text LIKE '%Dora Campos%'"
    search_db('master_index.db', q2)
