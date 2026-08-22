import sqlite3
from datetime import datetime, timezone

def add_alert():
    conn = sqlite3.connect('osint_app.db')
    c = conn.cursor()
    
    title = '🚨 TAXPAYER ALERT: Critical Data Exposure at Huntington Beach Police Department'
    summary = 'A comprehensive public infrastructure audit has revealed 41 open network ports on the Huntington Beach Police Department (hbpd.org) servers. Taxpayer data, including potentially sensitive law enforcement databases (SQL, MongoDB) and remote access points (RDP, SSH), are currently exposed to the open internet. This represents a massive attack surface and a severe failure to secure public data. View the Infrastructure tab for full details.'
    
    # Check if we already added it
    c.execute('SELECT id FROM investigations WHERE title=?', (title,))
    if not c.fetchone():
        c.execute('''
            INSERT INTO investigations (user_id, title, summary, is_public, timestamp)
            VALUES (1, ?, ?, 1, ?)
        ''', (title, summary, datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        print('Alert added successfully.')
    else:
        print('Alert already exists.')
    
    conn.close()

if __name__ == '__main__':
    add_alert()
