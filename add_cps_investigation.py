import sqlite3
from datetime import datetime, timezone

def add_investigation():
    conn = sqlite3.connect('osint_app.db')
    c = conn.cursor()
    
    title = '🚨 PUBLIC INVESTIGATION: The 23,000 Erased Children & The CPS Cover-Up'
    summary = 'In 2015, the CA DOJ altered its missing persons reporting to drop 4,700 male youth runaways per year. Concurrently, Orange County used deflated HUD statistics to claim only 700 homeless kids existed, while schools reported 23,000+. The state claimed databases were siloed, but CPS visit logs prove mandated reporters, housing, and law enforcement were actively interacting with these youth. The state did not lose 23,000 children; they mathematically erased them to hide systemic failure, fueling the 2018 adult homelessness epidemic.'
    
    c.execute('SELECT id FROM investigations WHERE title=?', (title,))
    if not c.fetchone():
        c.execute('''
            INSERT INTO investigations (user_id, title, summary, is_public, timestamp)
            VALUES (1, ?, ?, 1, ?)
        ''', (title, summary, datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        print('Investigation added successfully.')
    else:
        print('Investigation already exists.')
    
    conn.close()

if __name__ == '__main__':
    add_investigation()
