import sqlite3
import os

workspace_dir = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent"
db1_path = os.path.join(workspace_dir, "master_index.db")
db2_path = os.path.join(workspace_dir, "master_index_v2.db")

def copy_table_data(src_conn, dest_conn, table_name, dest_table_name):
    src_cursor = src_conn.cursor()
    dest_cursor = dest_conn.cursor()
    
    # Get table schema from source
    src_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    schema_row = src_cursor.fetchone()
    if not schema_row:
        print(f"Table {table_name} not found in source database.")
        return
        
    schema_sql = schema_row[0]
    # Replace table name in schema sql if necessary
    if table_name != dest_table_name:
        schema_sql = schema_sql.replace(f"CREATE TABLE {table_name}", f"CREATE TABLE {dest_table_name}")
        schema_sql = schema_sql.replace(f"CREATE TABLE `{table_name}`", f"CREATE TABLE `{dest_table_name}`")
        schema_sql = schema_sql.replace(f"CREATE TABLE [{table_name}]", f"CREATE TABLE [{dest_table_name}]")
    
    # Ensure IF NOT EXISTS is used
    schema_sql = schema_sql.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
        
    # Create table in destination
    dest_cursor.execute(schema_sql)
    
    # Get all rows
    src_cursor.execute(f"SELECT * FROM `{table_name}`")
    rows = src_cursor.fetchall()
    
    if not rows:
        print(f"No rows to copy for table {table_name}.")
        return
        
    # Build insert statement
    placeholders = ",".join(["?"] * len(rows[0]))
    insert_sql = f"INSERT OR IGNORE INTO `{dest_table_name}` VALUES ({placeholders})"
    
    dest_cursor.executemany(insert_sql, rows)
    dest_conn.commit()
    print(f"Copied {len(rows)} rows from {table_name} to {dest_table_name}.")

def merge_databases():
    print(f"Starting consolidation of database files...")
    
    if not os.path.exists(db1_path):
        print(f"Error: Legacy database {db1_path} not found.")
        return
        
    if not os.path.exists(db2_path):
        print(f"Error: Target database {db2_path} not found.")
        return

    # Open read-only connection to legacy database
    # URI mode allows us to specify read-only
    src_conn = sqlite3.connect(f"file:{db1_path}?mode=ro", uri=True)
    dest_conn = sqlite3.connect(db2_path)
    
    try:
        copy_table_data(src_conn, dest_conn, "MasterIndex", "MasterIndex")
        copy_table_data(src_conn, dest_conn, "document_scans", "document_scans")
        copy_table_data(src_conn, dest_conn, "nodes", "legacy_nodes")
        copy_table_data(src_conn, dest_conn, "node_timeline", "legacy_node_timeline")
        copy_table_data(src_conn, dest_conn, "node_relationships", "legacy_node_relationships")
    finally:
        src_conn.close()
        dest_conn.close()
        
    print("\nConsolidation complete!")
    print("Verification of new master_index_v2.db contents:")
    
    # Verify new counts
    conn = sqlite3.connect(db2_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        t_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM `{t_name}`")
        count = cursor.fetchone()[0]
        print(f"  Table: {t_name} | Rows: {count}")
    conn.close()

if __name__ == "__main__":
    merge_databases()
