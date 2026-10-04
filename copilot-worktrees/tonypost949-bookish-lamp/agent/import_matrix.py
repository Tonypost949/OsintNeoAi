import os
import sqlite3
import csv

input_file = r"C:\Users\HP\.gemini\antigravity-ide\brain\3a3fb7d5-104a-4ef7-8ddb-1d08eb64b1f5\.system_generated\steps\3279\content.md"
output_db = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\master_index.db"

def build_db():
    if os.path.exists(output_db):
        os.remove(output_db)
        
    conn = sqlite3.connect(output_db)
    cursor = conn.cursor()
    
    # Create the table
    cursor.execute('''
        CREATE TABLE MasterIndex (
            ENTITY_ID TEXT PRIMARY KEY,
            ENTITY_TYPE TEXT,
            ENTITY_NAME TEXT,
            PRIMARY_TAB TEXT,
            RELATED_IDS TEXT,
            LAST_UPDATED TEXT,
            SOURCE_DOC TEXT,
            NOTES TEXT,
            STATUS TEXT,
            PUBLIC_EVIDENCE TEXT,
            NON_PUBLIC_EVIDENCE TEXT
        )
    ''')
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find start of CSV data
    start_index = 0
    for i, line in enumerate(lines):
        if line.startswith("ENTITY_ID,ENTITY_TYPE"):
            start_index = i
            break
            
    # Extract CSV portion
    csv_lines = lines[start_index:]
    
    reader = csv.reader(csv_lines)
    header = next(reader) # Skip header
    
    rows_inserted = 0
    for row in reader:
        if not row or not row[0].strip():
            continue
        
        # Pad row if necessary
        while len(row) < 11:
            row.append("")
        
        # Ensure only 11 columns
        row = row[:11]
        
        try:
            cursor.execute('''
                INSERT INTO MasterIndex VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', row)
            rows_inserted += 1
        except Exception as e:
            print(f"Error inserting row {row[0]}: {e}")
            
    conn.commit()
    conn.close()
    print(f"Successfully inserted {rows_inserted} rows into {output_db}")

if __name__ == "__main__":
    build_db()
