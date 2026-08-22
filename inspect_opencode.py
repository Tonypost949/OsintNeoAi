import sqlite3, json
from pathlib import Path

db_path = Path('C:/Users/Amd949609/.local/share/opencode/opencode.db')
if not db_path.exists():
    print('Database not found')
    exit()

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute('SELECT name FROM sqlite_master WHERE type=" table\;')
tables = [row[0] for row in cursor.fetchall()]
print('Tables:', tables)

for t in tables:
 cursor.execute(f'PRAGMA table_info({t});')
 columns = [col[1] for col in cursor.fetchall()]
 print(f'\n=== Table: {t} (Columns: {columns}) ===')
 cursor.execute(f'SELECT * FROM {t} ORDER BY rowid DESC LIMIT 5;')
 for row in cursor.fetchall():
 print(row)
