import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# DB Path from utils.database (though we use sqlite3 directly as per rules)
DB_PATH = "data/osint_master.db"

def render():
    # --- Cyberpunk Styling ---
    st.markdown("""
    <style>
    .main {
        background-color: #0a0e1a;
        color: #c8d8f0;
    }
    .stTextInput > div > div > input {
        background-color: #0f1628;
        color: #00d4ff;
        border: 1px solid #1e2d50;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0a0e1a;
        border-bottom: 1px solid #1e2d50;
    }
    .stTabs [data-baseweb="tab"] {
        color: #c8d8f0;
    }
    .stTabs [aria-selected="true"] {
        color: #00d4ff !important;
        border-bottom-color: #00d4ff !important;
    }
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
        border: 1px solid #ff4b4b;
        padding: 2px 6px;
        border-radius: 4px;
        background: rgba(255, 75, 75, 0.1);
    }
    .risk-medium {
        color: #ffaa00;
        font-weight: bold;
        border: 1px solid #ffaa00;
        padding: 2px 6px;
        border-radius: 4px;
        background: rgba(255, 170, 0, 0.1);
    }
    .risk-low {
        color: #00ff88;
        font-weight: bold;
        border: 1px solid #00ff88;
        padding: 2px 6px;
        border-radius: 4px;
        background: rgba(0, 255, 136, 0.1);
    }
    .risk-unknown {
        color: #888888;
        font-weight: bold;
        border: 1px solid #888888;
        padding: 2px 6px;
        border-radius: 4px;
        background: rgba(136, 136, 136, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🔍 Advanced Global Search")
    
    # --- Sidebar Filters ---
    st.sidebar.header("Global Filters")
    
    # Initialize session state for report queue if not exists
    if "report_queue" not in st.session_state:
        st.session_state["report_queue"] = set()

    # Get unique entity types for filter
    try:
        conn = sqlite3.connect(DB_PATH)
        types_res = conn.execute("SELECT DISTINCT type FROM entities WHERE type IS NOT NULL").fetchall()
        entity_types = [r[0] for r in types_res]
        conn.close()
    except:
        entity_types = ["Person", "Location", "Organization", "Email", "IP", "Domain", "Phone", "Document", "Legal", "Vehicle", "Device"]

    selected_types = st.sidebar.multiselect("Entity Types", options=entity_types, default=entity_types)
    selected_risks = st.sidebar.multiselect("Risk Levels", options=["High", "Medium", "Low", "Unknown"], default=["High", "Medium", "Low", "Unknown"])
    
    date_range = st.sidebar.date_input("Event Date Range", value=[datetime(2000, 1, 1), datetime.now()])

    # --- Search Bar ---
    search_query = st.text_input("Search OSINT Database...", placeholder="Enter keywords, names, IDs, locations...")

    if search_query:
        query_wildcard = f"%{search_query}%"
        
        # Results container
        results = {
            "entities": [],
            "relationships": [],
            "events": [],
            "file_scans": []
        }

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        # 1. Entities Search
        # searches label, notes, source, geo_location, entity_id columns
        ent_sql = """
            SELECT * FROM entities 
            WHERE (label LIKE ? OR notes LIKE ? OR source LIKE ? OR geo_location LIKE ? OR entity_id LIKE ?)
        """
        ent_rows = conn.execute(ent_sql, [query_wildcard]*5).fetchall()
        results["entities"] = [dict(r) for r in ent_rows if r['type'] in selected_types and r['risk_level'] in selected_risks]

        # 2. Relationships Search
        # searches source_entity, target_entity, relationship_type
        rel_sql = """
            SELECT * FROM relationships 
            WHERE (source_entity LIKE ? OR target_entity LIKE ? OR relationship_type LIKE ?)
        """
        rel_rows = conn.execute(rel_sql, [query_wildcard]*3).fetchall()
        results["relationships"] = [dict(r) for r in rel_rows]

        # 3. Events Search
        # searches description, location, entities_involved, event_type
        # (Note: description maps to event_type or some other field if not available, but instructions say description)
        # Checking schema: id, event_id, timestamp, event_type, location, entities_involved, source, created_at
        # We'll search event_type as description proxy if no description column exists.
        ev_sql = """
            SELECT * FROM events 
            WHERE (event_type LIKE ? OR location LIKE ? OR entities_involved LIKE ? OR source LIKE ?)
        """
        ev_rows = conn.execute(ev_sql, [query_wildcard]*4).fetchall()
        
        # Filter events by date if possible
        filtered_events = []
        for r in ev_rows:
            try:
                # Handle varying date formats
                ev_date = pd.to_datetime(r['timestamp']).date()
                can_filter = False
                if isinstance(date_range, (list, tuple)) and len(date_range) >= 2:
                    start_date = date_range[0]
                    end_date = date_range[1]
                    can_filter = True
                
                if can_filter:
                    if start_date <= ev_date <= end_date:
                        filtered_events.append(dict(r))
                else:
                    filtered_events.append(dict(r))
            except:
                filtered_events.append(dict(r))
        results["events"] = filtered_events

        # 4. File Scans Search
        # searches file_name, names_found, orgs_found, keywords_hit, content_preview, case_numbers
        # Check if columns exist in file_scan_results
        try:
            fs_sql = """
                SELECT * FROM file_scan_results 
                WHERE (file_path LIKE ? OR names_found LIKE ? OR orgs_found LIKE ? OR keywords_hit LIKE ? OR content_preview LIKE ? OR case_numbers LIKE ?)
            """
            fs_rows = conn.execute(fs_sql, [query_wildcard]*6).fetchall()
            results["file_scans"] = [dict(r) for r in fs_rows if r.get('risk_flag', 'Unknown') in selected_risks]
        except sqlite3.OperationalError:
            # Fallback if columns don't exist yet (T005 might create them later)
            # Schema from rules: id, file_name, file_path, file_type, file_size, category, risk_flag, names_found, orgs_found, case_numbers, keywords_hit, content_preview, gps_lat, gps_lon, gps_location, camera_make, camera_model, audio_artist, audio_title, md5_hash, scan_date
            fs_sql = "SELECT * FROM file_scan_results WHERE file_path LIKE ?"
            fs_rows = conn.execute(fs_sql, [query_wildcard]).fetchall()
            results["file_scans"] = [dict(r) for r in fs_rows]

        conn.close()

        # --- Display Results ---
        tab1, tab2, tab3, tab4 = st.tabs([
            f"Entities ({len(results['entities'])})", 
            f"Relationships ({len(results['relationships'])})", 
            f"Events ({len(results['events'])})", 
            f"File Scans ({len(results['file_scans'])})"
        ])

        def risk_badge(level):
            level = str(level).capitalize()
            if level == "High": return f'<span class="risk-high">{level}</span>'
            if level == "Medium": return f'<span class="risk-medium">{level}</span>'
            if level == "Low": return f'<span class="risk-low">{level}</span>'
            return f'<span class="risk-unknown">{level}</span>'

        with tab1:
            if not results["entities"]:
                st.info("No entities found matching your search.")
            else:
                for ent in results["entities"]:
                    col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
                    with col1:
                        if st.checkbox("", key=f"ent_chk_{ent['id']}", value=(ent['entity_id'] in st.session_state["report_queue"])):
                            st.session_state["report_queue"].add(ent['entity_id'])
                        else:
                            st.session_state["report_queue"].discard(ent['entity_id'])
                    with col2:
                        st.markdown(f"**{ent['label']}** ({ent['entity_id']}) - *{ent['type']}*")
                        st.caption(f"Source: {ent['source']} | Loc: {ent['geo_location']}")
                    with col3:
                        st.markdown(risk_badge(ent['risk_level']), unsafe_allow_html=True)
                    st.divider()

        with tab2:
            if not results["relationships"]:
                st.info("No relationships found.")
            else:
                for rel in results["relationships"]:
                    st.markdown(f"**{rel['source_entity']}** → `{rel['relationship_type']}` → **{rel['target_entity']}**")
                    st.caption(f"Confidence: {rel['confidence']} | Source: {rel['source']}")
                    st.divider()

        with tab3:
            if not results["events"]:
                st.info("No events found.")
            else:
                for ev in results["events"]:
                    st.markdown(f"**{ev['event_type']}** @ {ev['location']}")
                    st.caption(f"Timestamp: {ev['timestamp']} | Entities: {ev['entities_involved']}")
                    st.divider()

        with tab4:
            if not results["file_scans"]:
                st.info("No file scans found.")
            else:
                for fs in results["file_scans"]:
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        # Fallback for file_name if not in DB yet
                        fname = fs.get('file_name', fs['file_path'].split('/')[-1])
                        st.markdown(f"📄 **{fname}** ({fs.get('file_type', 'UNK')})")
                        st.caption(f"Path: {fs['file_path']}")
                        if fs.get('names_found'): st.caption(f"Names: {fs['names_found']}")
                    with col2:
                        st.markdown(risk_badge(fs.get('risk_flag', 'Unknown')), unsafe_allow_html=True)
                    st.divider()
    else:
        st.info("Enter a search term above to begin querying the global intelligence database.")

if __name__ == "__main__":
    render()
