import csv
import json
import sqlite3
import os

# Define paths
nodes_csv = 'C:/Amd949609_Antigravity_v1/user_nodes.csv'
db_path = 'C:/OsintNeoAi/osint_vector_index.db'
server_script = 'C:/OsintNeoAi/osint_geospatial_server.py'

# 1. Create SQLite Vector / Keyword Index DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS osint_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT,
        url TEXT,
        type TEXT,
        source TEXT
    )
''')
cursor.execute('DELETE FROM osint_nodes')

with open(nodes_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    to_db = [(r['Label'], r['URL'], r['Type'], r['Source']) for r in reader]

cursor.executemany('INSERT INTO osint_nodes (label, url, type, source) VALUES (?, ?, ?, ?)', to_db)
conn.commit()
conn.close()

print(f"Indexed {len(to_db)} nodes into SQLite vector database at {db_path}")

# 2. Update Python server to expose /api/nodes endpoint for Copilot agents & VM/VPS sync
with open(server_script, 'r', encoding='utf-8') as f:
    server_code = f.read()

if '/api/nodes' not in server_code:
    new_endpoint = '''
    elif self.path.startswith('/api/nodes'):
        conn = sqlite3.connect('C:/OsintNeoAi/osint_vector_index.db')
        c = conn.cursor()
        c.execute('SELECT label, url, type, source FROM osint_nodes LIMIT 500')
        rows = c.fetchall()
        conn.close()
        nodes_list = [{'label': r[0], 'url': r[1], 'type': r[2], 'source': r[3]} for r in rows]
        self._send_json({'status': 'success', 'count': len(nodes_list), 'nodes': nodes_list})
'''
    server_code = server_code.replace("self._send_json({'error': 'Endpoint not found'}, 404)", new_endpoint + "\n        self._send_json({'error': 'Endpoint not found'}, 404)")
    with open(server_script, 'w', encoding='utf-8') as f:
        f.write(server_code)

print("Server script updated with /api/nodes endpoint for Copilot agents and VM/VPS sync.")
