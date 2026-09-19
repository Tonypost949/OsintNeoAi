import sqlite3
import json

def init_audit_table():
    conn = sqlite3.connect('osint_app.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS infrastructure_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity TEXT,
            domain TEXT,
            ip TEXT,
            port INTEGER,
            service TEXT,
            status TEXT,
            risk TEXT
        )
    ''')
    
    # Load JSON
    with open('infrastructure_audit_parsed.json', 'r', encoding='utf-8') as f:
        records = json.load(f)
        
    for r in records:
        # Check if exists
        c.execute('SELECT id FROM infrastructure_audits WHERE entity=? AND port=?', (r['entity'], r['port']))
        if not c.fetchone():
            c.execute('''
                INSERT INTO infrastructure_audits (entity, domain, ip, port, service, status, risk)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (r['entity'], r['domain'], r['ip'], r['port'], r['service'], r['status'], r['risk']))
            
    conn.commit()
    conn.close()
    print("Audit data loaded into SQLite.")

if __name__ == "__main__":
    init_audit_table()
