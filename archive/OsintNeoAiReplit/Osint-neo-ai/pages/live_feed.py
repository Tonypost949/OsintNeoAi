import streamlit as st
import sqlite3
import pandas as pd
import json
import os
import time
from datetime import datetime

# DB Path
DB_PATH = "data/osint_master.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data(ttl=60)
def get_existing_md5s():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT md5_hash FROM file_scan_results")
    rows = cursor.fetchall()
    conn.close()
    return {row['md5_hash'] for row in rows if row['md5_hash']}

@st.cache_data(ttl=60)
def get_recent_scans(limit=50):
    conn = get_db_connection()
    query = "SELECT * FROM file_scan_results ORDER BY created_at DESC LIMIT ?"
    # Use standard sqlite3 fetch then convert to DataFrame to avoid type issues with read_sql_query
    cursor = conn.cursor()
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    conn.close()
    if rows:
        return pd.DataFrame([dict(row) for row in rows])
    return pd.DataFrame()

def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total_files = cursor.execute("SELECT COUNT(*) FROM file_scan_results").fetchone()[0]
    high_risk = cursor.execute("SELECT COUNT(*) FROM file_scan_results WHERE risk_flag = 'High'").fetchone()[0]
    
    # Files added today (assuming created_at is YYYY-MM-DD HH:MM:SS)
    today = datetime.now().strftime('%Y-%m-%d')
    added_today = cursor.execute("SELECT COUNT(*) FROM file_scan_results WHERE created_at LIKE ?", (f"{today}%",)).fetchone()[0]
    
    conn.close()
    return total_files, high_risk, added_today

def infer_category(extension):
    ext = extension.lower().strip('.')
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']:
        return 'Images'
    if ext in ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'html', 'htm']:
        return 'Documents'
    if ext in ['mp3', 'wav', 'ogg', 'm4a', 'flac']:
        return 'Audio'
    if ext in ['mp4', 'mkv', 'avi', 'mov', 'wmv']:
        return 'Video'
    if ext in ['py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'sh', 'json', 'xml', 'zip', 'tar', 'gz']:
        return 'Code/Archive'
    return 'Other'

def infer_risk(path):
    keywords = ['password', 'secret', 'private', 'key', 'credentials', 'ssn', 'dob', 'confidential']
    path_lower = path.lower()
    if any(k in path_lower for k in keywords):
        return 'High'
    return 'Low'

def render():
    st.markdown("""
        <style>
        .stApp {
            background-color: #0a0e1a;
            color: #c8d8f0;
        }
        [data-testid="stSidebar"] {
            background-color: #0f1628;
            border-right: 1px solid #1e2d50;
        }
        .stButton>button {
            background-color: #1e2d50;
            color: #00d4ff;
            border: 1px solid #00d4ff;
        }
        .stDataFrame {
            border: 1px solid #1e2d50;
        }
        h1, h2, h3 {
            color: #00d4ff !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📡 Live Feed Monitor")

    tab1, tab2 = st.tabs(["Upload Monitor", "Activity Log"])

    with tab1:
        st.header("Upload Monitor")
        uploaded_file = st.file_uploader("Upload master_index.json", type=['json'])

        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                fingerprints = data.get("fingerprints", [])
                
                existing_md5s = get_existing_md5s()
                
                new_files = []
                already_in_db = 0
                
                for fp in fingerprints:
                    if '|' in fp:
                        path, md5 = fp.split('|', 1)
                        if md5 in existing_md5s:
                            already_in_db += 1
                        else:
                            file_name = os.path.basename(path)
                            ext = os.path.splitext(file_name)[1]
                            new_files.append({
                                "file_path": path,
                                "file_name": file_name,
                                "file_type": ext,
                                "md5_hash": md5,
                                "category": infer_category(ext),
                                "risk_flag": infer_risk(path)
                            })
                    else:
                        # Handle cases where format might be different or md5 is missing
                        pass

                st.info(f"🔍 {len(new_files)} new files detected, {already_in_db} already in database")

                if new_files:
                    st.subheader("Preview of New Files")
                    preview_df = pd.DataFrame(new_files)
                    st.dataframe(preview_df[["file_path", "category", "risk_flag"]])

                    if st.button("Import New Files"):
                        progress_bar = st.progress(0)
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        total_new = len(new_files)
                        for i, f in enumerate(new_files):
                            cursor.execute("""
                                INSERT INTO file_scan_results 
                                (file_path, file_name, file_type, category, risk_flag, names_found, orgs_found, md5_hash)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                f['file_path'], 
                                f['file_name'], 
                                f['file_type'], 
                                f['category'], 
                                f['risk_flag'], 
                                "", # names_found
                                "", # orgs_found
                                f['md5_hash']
                            ))
                            progress_bar.progress((i + 1) / total_new)
                        
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Successfully imported {total_new} files.")
                        st.cache_data.clear() # Clear cache to refresh stats and log
                else:
                    st.write("No new files to import.")

            except Exception as e:
                st.error(f"Error parsing JSON: {e}")

    with tab2:
        st.header("Activity Log")
        
        # Stats
        total, high, today = get_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Files", total)
        col2.metric("High Risk", high)
        col3.metric("Added Today", today)

        # Controls
        c1, c2 = st.columns([1, 4])
        if c1.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()
        
        auto_refresh = c2.toggle("Auto-refresh (30s)")
        
        # Log Table
        df = get_recent_scans()
        
        if not df.empty:
            def style_risk(row):
                return ['background-color: #440000' if row.risk_flag == 'High' else '' for _ in row]

            st.dataframe(df.style.apply(style_risk, axis=1), use_container_width=True)
        else:
            st.write("No activity recorded yet.")

        if auto_refresh:
            time.sleep(30)
            st.rerun()

if __name__ == "__main__":
    render()
