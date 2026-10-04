import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import streamlit.components.v1 as components
import folium
from utils.database import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data(ttl=60)
def get_entities_list():
    conn = get_db_connection()
    entities = conn.execute("SELECT label, entity_id FROM entities ORDER BY label ASC").fetchall()
    conn.close()
    return [dict(e) for e in entities]

@st.cache_data(ttl=60)
def get_entity_details(entity_id):
    conn = get_db_connection()
    entity = conn.execute("SELECT * FROM entities WHERE entity_id = ?", (entity_id,)).fetchone()
    conn.close()
    return dict(entity) if entity else None

@st.cache_data(ttl=60)
def get_entity_connections(entity_label):
    conn = get_db_connection()
    query = """
    SELECT * FROM relationships 
    WHERE source_entity = ? OR target_entity = ?
    """
    rels = conn.execute(query, (entity_label, entity_label)).fetchall()
    conn.close()
    return [dict(r) for r in rels]

@st.cache_data(ttl=60)
def get_entity_events(entity_label):
    conn = get_db_connection()
    query = "SELECT * FROM events WHERE entities_involved LIKE ?"
    events = conn.execute(query, (f"%{entity_label}%",)).fetchall()
    conn.close()
    return [dict(e) for e in events]

@st.cache_data(ttl=60)
def get_entity_files(entity_label):
    conn = get_db_connection()
    # file_scan_results schema from task description: 
    # id, file_name, file_path, file_type, file_size, category, risk_flag, names_found, orgs_found, case_numbers, keywords_hit, content_preview, gps_lat, gps_lon, gps_location, camera_make, camera_model, audio_artist, audio_title, md5_hash, scan_date
    try:
        query = "SELECT * FROM file_scan_results WHERE names_found LIKE ? OR orgs_found LIKE ?"
        files = conn.execute(query, (f"%{entity_label}%", f"%{entity_label}%")).fetchall()
        return [dict(f) for f in files]
    except sqlite3.OperationalError:
        # If columns don't exist yet, we'll try to find mentions in metadata_json if it exists
        try:
            query = "SELECT * FROM file_scan_results WHERE metadata_json LIKE ?"
            files = conn.execute(query, (f"%{entity_label}%",)).fetchall()
            return [dict(f) for f in files]
        except sqlite3.OperationalError:
            return []
    finally:
        conn.close()

def update_entity_notes(entity_id, notes):
    conn = get_db_connection()
    conn.execute("UPDATE entities SET notes = ? WHERE entity_id = ?", (notes, entity_id))
    conn.commit()
    conn.close()
    st.cache_data.clear()

def render_map(geo_location):
    if not geo_location:
        return None
    try:
        # Try "lat, lon" format
        parts = geo_location.replace(" ", "").split(",")
        if len(parts) == 2:
            lat, lon = float(parts[0]), float(parts[1])
        else:
            # Maybe it's a name like "Santa Ana, CA" - we don't have a geocoder here
            # For now, only support lat/lon for the map as per instructions
            return None
            
        m = folium.Map(location=[lat, lon], zoom_start=12, tiles="CartoDB dark_matter")
        folium.Marker([lat, lon]).add_to(m)
        return m.get_root().render()
    except Exception:
        return None

def render_connections_chart(entity_label, relationships):
    if not relationships:
        st.info("No connections found for this entity.")
        return

    # Simple plotly network-style scatter chart
    # Nodes as scatter points, edges as lines
    
    nodes: dict[str, tuple[float, float]] = {entity_label: (0.0, 0.0)}
    edges = []
    
    # Place neighbors in a circle
    import math
    for i, rel in enumerate(relationships):
        neighbor = str(rel['target_entity'] if rel['source_entity'] == entity_label else rel['source_entity'])
        if neighbor not in nodes:
            angle = 2 * math.pi * i / len(relationships)
            nodes[neighbor] = (math.cos(angle), math.sin(angle))
        edges.append((entity_label, neighbor, rel['relationship_type']))

    edge_x = []
    edge_y = []
    for start_node, end_node, rel_type in edges:
        x0, y0 = nodes[start_node]
        x1, y1 = nodes[end_node]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#00d4ff'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node, pos in nodes.items():
        node_x.append(pos[0])
        node_y.append(pos[1])
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker=dict(
            showscale=False,
            color='#00d4ff',
            size=20,
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0,l=0,r=0,t=0),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    st.plotly_chart(fig, use_container_width=True)

def render():
    st.markdown("""
        <style>
        .main {
            background-color: #0a0e1a;
            color: #c8d8f0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #0f1628;
            border: 1px solid #1e2d50;
            border-radius: 4px 4px 0px 0px;
            color: #c8d8f0;
            padding: 10px 20px;
        }
        .stTabs [aria-selected="true"] {
            border-bottom: 2px solid #00d4ff !important;
            background-color: #1e2d50;
        }
        .dossier-card {
            background-color: #0f1628;
            border: 1px solid #1e2d50;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .risk-high { border-left: 5px solid #ff4b4b; }
        .risk-medium { border-left: 5px solid #ffaa00; }
        .risk-low { border-left: 5px solid #00ff88; }
        .risk-unknown { border-left: 5px solid #888888; }
        
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .badge-high { background-color: #ff4b4b; color: white; }
        .badge-medium { background-color: #ffaa00; color: white; }
        .badge-low { background-color: #00ff88; color: #0a0e1a; }
        .badge-unknown { background-color: #888888; color: white; }
        </style>
    """, unsafe_allow_html=True)

    st.title("👤 Person Deep-Dive")
    
    entities = get_entities_list()
    options = {f"{e['label']} ({e['entity_id']})": e['entity_id'] for e in entities}
    
    selected_label = st.selectbox("Select Entity", options.keys())
    
    if selected_label:
        entity_id = options[selected_label]
        entity = get_entity_details(entity_id)
        
        if entity:
            risk = entity.get('risk_level', 'Unknown')
            risk_class = f"risk-{risk.lower()}"
            badge_class = f"badge-{risk.lower()}"
            
            # Header card
            st.markdown(f"""
                <div class="dossier-card {risk_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h2 style="margin:0; color:#00d4ff;">{entity['label']}</h2>
                            <code style="color:#888888;">{entity['entity_id']}</code>
                        </div>
                        <div style="text-align: right;">
                            <span class="badge {badge_class}">{risk} Risk</span><br>
                            <small style="color:#888888;">Type: {entity['type']}</small>
                        </div>
                    </div>
                    <hr style="border-color: #1e2d50;">
                    <div style="display: flex; gap: 40px;">
                        <div>
                            <p style="margin:0; color:#888888; font-size:0.8em;">SOURCE</p>
                            <p style="margin:0;">{entity['source']}</p>
                        </div>
                        <div>
                            <p style="margin:0; color:#888888; font-size:0.8em;">CREATED</p>
                            <p style="margin:0;">{entity['created_at']}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            tabs = st.tabs(["📊 Profile", "🔗 Connections", "📅 Events", "📁 Files", "📝 Notes"])
            
            with tabs[0]:
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("### Profile Information")
                    st.json({k: v for k, v in entity.items() if v and k not in ['id', 'notes']})
                
                with col2:
                    st.markdown("### Location")
                    geo = entity.get('geo_location')
                    if geo:
                        st.write(f"**Coordinates/Address:** {geo}")
                        map_html = render_map(geo)
                        if map_html:
                            components.html(map_html, height=300)
                        else:
                            st.info("Map not available for this location format.")
                    else:
                        st.info("No geo-location data available.")

            with tabs[1]:
                st.markdown("### Entity Connections")
                rels = get_entity_connections(entity['label'])
                if rels:
                    render_connections_chart(entity['label'], rels)
                    st.table(pd.DataFrame(rels)[['source_entity', 'target_entity', 'relationship_type', 'confidence', 'source']])
                else:
                    st.info("No connections found.")

            with tabs[2]:
                st.markdown("### Related Events")
                events = get_entity_events(entity['label'])
                if events:
                    st.table(pd.DataFrame(events)[['timestamp', 'event_type', 'location', 'entities_involved', 'source']])
                else:
                    st.info("No events found.")

            with tabs[3]:
                st.markdown("### Related Files")
                files = get_entity_files(entity['label'])
                if files:
                    # Apply risk color to rows (simplified for table)
                    df_files = pd.DataFrame(files)
                    st.table(df_files[['file_name', 'category', 'risk_flag', 'scan_date']] if 'file_name' in df_files.columns else df_files)
                else:
                    st.info("No file scan results found.")

            with tabs[4]:
                st.markdown("### Entity Notes")
                current_notes = entity.get('notes', '')
                new_notes = st.text_area("Edit Notes", value=current_notes, height=200)
                if st.button("Save Notes"):
                    update_entity_notes(entity_id, new_notes)
                    st.success("Notes updated successfully!")
                    st.rerun()

if __name__ == "__main__":
    render()
