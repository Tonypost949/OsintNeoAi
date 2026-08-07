import streamlit as st
import sqlite3
import pandas as pd
from utils.report_builder import build_report

# Cyberpunk Theme Styles
CYBERPUNK_STYLE = """
<style>
    .stApp {
        background-color: #0a0e1a;
        color: #c8d8f0;
    }
    .stHeader {
        color: #00d4ff;
    }
    .stButton>button {
        background-color: #1e2d50;
        color: #00d4ff;
        border: 1px solid #00d4ff;
    }
    .stCheckbox {
        color: #c8d8f0;
    }
    .report-card {
        background-color: #0f1628;
        border: 1px solid #1e2d50;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .risk-high { color: #ff4b4b; border-left: 5px solid #ff4b4b; }
    .risk-medium { color: #ffaa00; border-left: 5px solid #ffaa00; }
    .risk-low { color: #00ff88; border-left: 5px solid #00ff88; }
</style>
"""

@st.cache_data(ttl=60)
def get_all_entities():
    conn = sqlite3.connect('data/osint_master.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entities")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

@st.cache_data(ttl=60)
def get_related_data(entity_labels):
    conn = sqlite3.connect('data/osint_master.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    placeholders = ', '.join(['?'] * len(entity_labels))
    
    # Get relationships
    cursor.execute(f"SELECT * FROM relationships WHERE source_entity IN ({placeholders}) OR target_entity IN ({placeholders})", entity_labels + entity_labels)
    relationships = [dict(row) for row in cursor.fetchall()]
    
    # Get events
    events = []
    for label in entity_labels:
        cursor.execute("SELECT * FROM events WHERE entities_involved LIKE ?", (f'%{label}%',))
        events.extend([dict(row) for row in cursor.fetchall()])
    
    # Get file scans
    file_scans = []
    for label in entity_labels:
        cursor.execute("SELECT * FROM file_scan_results WHERE names_found LIKE ? OR orgs_found LIKE ?", (f'%{label}%', f'%{label}%'))
        file_scans.extend([dict(row) for row in cursor.fetchall()])
        
    conn.close()
    
    # Deduplicate events and file scans by ID
    events = list({v['id']: v for v in events}.values())
    file_scans = list({v['id']: v for v in file_scans}.values())
    
    return relationships, events, file_scans

def render():
    st.markdown(CYBERPUNK_STYLE, unsafe_allow_html=True)
    st.title("📄 PDF Report Generator")
    st.markdown("---")

    entities = get_all_entities()
    if not entities:
        st.warning("No entities found in database.")
        return

    # Session state for selection
    if "selected_entities" not in st.session_state:
        st.session_state["selected_entities"] = set()
    
    # Pull from report_queue if available
    queue = st.session_state.get("report_queue", set())
    if queue:
        st.session_state["selected_entities"].update(queue)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🔍 Select Entities")
        
        c1, c2 = st.columns(2)
        if c1.button("Select All High Risk"):
            high_risk_ids = {e['label'] for e in entities if e.get('risk_level') == 'High'}
            st.session_state["selected_entities"].update(high_risk_ids)
            st.rerun()
            
        if c2.button("Clear All"):
            st.session_state["selected_entities"] = set()
            if "report_queue" in st.session_state:
                st.session_state["report_queue"] = set()
            st.rerun()

        # Group by type
        entity_types = sorted(list(set(e['type'] for e in entities)))
        for etype in entity_types:
            with st.expander(f"{etype}s"):
                type_entities = [e for e in entities if e['type'] == etype]
                for e in type_entities:
                    label = e['label']
                    is_selected = label in st.session_state["selected_entities"]
                    if st.checkbox(f"{label} ({e['risk_level']})", value=is_selected, key=f"chk_{label}"):
                        st.session_state["selected_entities"].add(label)
                    else:
                        st.session_state["selected_entities"].discard(label)

    with col2:
        st.subheader("⚙️ Report Options")
        report_title = st.text_input("Report Title", value="Intelligence Briefing")
        author = st.text_input("Author", value="OSINT AI Analyst")
        classification = st.selectbox("Classification", ["CONFIDENTIAL", "SECRET", "TOP SECRET", "UNCLASSIFIED"])
        
        include_sections = {
            "Entities": st.checkbox("Entities", value=True),
            "Relationships": st.checkbox("Relationships", value=True),
            "Events": st.checkbox("Events", value=True),
            "Files": st.checkbox("File Scans", value=True)
        }

        st.markdown("---")
        st.subheader("👁️ Preview")
        selected_labels = list(st.session_state["selected_entities"])
        if not selected_labels:
            st.info("No entities selected.")
        else:
            selected_data = [e for e in entities if e['label'] in selected_labels]
            for e in selected_data:
                risk_class = f"risk-{e['risk_level'].lower()}" if e['risk_level'] else ""
                st.markdown(f"""
                <div class="report-card {risk_class}">
                    <strong>{e['label']}</strong><br>
                    <small>Type: {e['type']} | Risk: {e['risk_level']}</small>
                </div>
                """, unsafe_allow_html=True)

            if st.button("Generate Report"):
                with st.spinner("Generating PDF..."):
                    relationships, events, file_scans = get_related_data(selected_labels)
                    
                    # Filter based on user selection
                    if not include_sections["Relationships"]: relationships = []
                    if not include_sections["Events"]: events = []
                    if not include_sections["Files"]: file_scans = []
                    
                    pdf_bytes = build_report(
                        selected_data, 
                        relationships, 
                        events, 
                        file_scans, 
                        report_title, 
                        author, 
                        classification
                    )
                    
                    st.success("Report Generated!")
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"OSINT_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    render()
