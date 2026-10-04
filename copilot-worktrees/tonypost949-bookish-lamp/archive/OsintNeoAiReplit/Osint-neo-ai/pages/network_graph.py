import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import time

def get_connection():
    conn = sqlite3.connect("data/osint_master.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()
    entities = pd.read_sql_query("SELECT * FROM entities", conn)
    relationships = pd.read_sql_query("SELECT * FROM relationships", conn)
    conn.close()
    return entities, relationships

def fruchterman_reingold(nodes, edges, iterations=50, k=1.0, area=1000):
    """Simple spring/force layout algorithm."""
    # Initialize positions randomly
    pos = {node: np.random.rand(2) * 100 for node in nodes}
    
    # Pre-calculate adjacent nodes
    adj = {node: set() for node in nodes}
    for _, edge in edges.iterrows():
        if edge['source_entity'] in adj and edge['target_entity'] in adj:
            adj[edge['source_entity']].add(edge['target_entity'])
            adj[edge['target_entity']].add(edge['source_entity'])

    # Constants
    k = k * np.sqrt(area / len(nodes))
    t = 10.0  # Temperature
    dt = t / (iterations + 1)

    for i in range(iterations):
        # Repulsion forces
        disp = {node: np.zeros(2) for node in nodes}
        for v in nodes:
            for u in nodes:
                if v != u:
                    diff = pos[v] - pos[u]
                    dist = np.linalg.norm(diff)
                    if dist > 0:
                        disp[v] += (diff / dist) * (k**2 / dist)
        
        # Attraction forces
        for _, edge in edges.iterrows():
            v = edge['source_entity']
            u = edge['target_entity']
            if v in pos and u in pos:
                diff = pos[v] - pos[u]
                dist = np.linalg.norm(diff)
                if dist > 0:
                    force = (dist**2) / k
                    disp[v] -= (diff / dist) * force
                    disp[u] += (diff / dist) * force
        
        # Update positions
        for v in nodes:
            dist = np.linalg.norm(disp[v])
            if dist > 0:
                pos[v] += (disp[v] / dist) * min(dist, t)
            
            # Keep within bounds
            pos[v] = np.clip(pos[v], 0, 100)
            
        t -= dt

    return pos

def render():
    st.markdown("""
    <style>
        .stApp { background-color: #0a0e1a; }
        h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New', monospace; }
        .stMarkdown { color: #c8d8f0; }
        
        /* Cyberpunk Panel */
        .cyber-panel {
            background: #0f1628;
            border: 1px solid #1e2d50;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.05);
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🕸️ NETWORK GRAPH")
    st.caption("INTERACTIVE ENTITY RELATIONSHIP VISUALIZER")

    # Load data
    entities_df, relationships_df = load_data()

    if entities_df.empty:
        st.warning("No entities found in database.")
        return

    # Sidebar Filters
    with st.sidebar:
        st.header("Graph Controls")
        
        # Filter by entity type
        all_types = sorted(entities_df['type'].unique().tolist())
        selected_types = st.multiselect("Entity Types", all_types, default=all_types)
        
        # Filter by risk level
        all_risks = sorted(entities_df['risk_level'].unique().tolist())
        selected_risks = st.multiselect("Risk Levels", all_risks, default=all_risks)
        
        # Connection count
        conn_counts = {}
        for _, rel in relationships_df.iterrows():
            conn_counts[rel['source_entity']] = conn_counts.get(rel['source_entity'], 0) + 1
            conn_counts[rel['target_entity']] = conn_counts.get(rel['target_entity'], 0) + 1
            
        min_conns = st.sidebar.slider("Min Connections", 0, 10, 0)
        
        # Isolate Node
        isolate_label = st.text_input("Isolate Node (Label)", "")

    # Apply Filters
    filtered_entities = entities_df[
        (entities_df['type'].isin(selected_types)) & 
        (entities_df['risk_level'].isin(selected_risks))
    ].copy()
    
    # Filter by connections
    if min_conns > 0:
        filtered_entities = filtered_entities[filtered_entities['entity_id'].apply(lambda x: conn_counts.get(x, 0) >= min_conns)]

    # Get valid entity IDs
    valid_ids = set(filtered_entities['entity_id'].tolist())
    
    # Filter relationships to only include filtered entities
    filtered_rels = relationships_df[
        (relationships_df['source_entity'].isin(valid_ids)) & 
        (relationships_df['target_entity'].isin(valid_ids))
    ].copy()

    if filtered_entities.empty:
        st.info("No entities match the current filters.")
        return

    # Layout calculation
    node_ids = filtered_entities['entity_id'].tolist()
    pos = fruchterman_reingold(node_ids, filtered_rels)

    # Prepare Graph
    edge_x = []
    edge_y = []
    edge_text = []
    
    # Highlighting logic
    highlight_ids = set()
    is_isolating = False
    if isolate_label:
        matching = filtered_entities[filtered_entities['label'].str.contains(isolate_label, case=False)]
        if not matching.empty:
            is_isolating = True
            for _, row in matching.iterrows():
                eid = row['entity_id']
                highlight_ids.add(eid)
                # Add neighbors
                neighbors = filtered_rels[filtered_rels['source_entity'] == eid]['target_entity'].tolist()
                neighbors += filtered_rels[filtered_rels['target_entity'] == eid]['source_entity'].tolist()
                highlight_ids.update(neighbors)

    # Node Colors Map
    color_map = {
        "Person": "#00d4ff",
        "Organization": "#ff6b35",
        "Location": "#00ff88",
        "Email": "#ff4b4b",
        "IP": "#ffaa00",
        "Domain": "#aa44ff"
    }
    default_color = "#888888"

    # Confidence Map
    confidence_map = {"High": 3, "Medium": 2, "Low": 1}

    # Create Edges
    edge_traces = []
    for _, edge in filtered_rels.iterrows():
        x0, y0 = pos[edge['source_entity']]
        x1, y1 = pos[edge['target_entity']]
        
        opacity = 1.0
        if is_isolating:
            if edge['source_entity'] not in highlight_ids or edge['target_entity'] not in highlight_ids:
                opacity = 0.2
        
        width = confidence_map.get(edge['confidence'], 1)
        
        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=width, color=f'rgba(120,120,120,{opacity})'),
            hoverinfo='text',
            text=f"Type: {edge['relationship_type']}<br>Confidence: {edge['confidence']}",
            mode='lines'
        ))

    # Create Nodes
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    node_opacity = []

    for _, node in filtered_entities.iterrows():
        eid = node['entity_id']
        nx, ny = pos[eid]
        node_x.append(nx)
        node_y.append(ny)
        node_text.append(f"Label: {node['label']}<br>Type: {node['type']}<br>Risk: {node['risk_level']}<br>Source: {node['source']}")
        
        node_color.append(color_map.get(node['type'], default_color))
        
        # Size by connections
        c_count = conn_counts.get(eid, 0)
        size = 10 + min(c_count * 5, 30)
        node_size.append(size)
        
        if is_isolating:
            node_opacity.append(1.0 if eid in highlight_ids else 0.2)
        else:
            node_opacity.append(1.0)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            opacity=node_opacity,
            line_width=2))

    fig = go.Figure(data=edge_traces + [node_trace],
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0,l=0,r=0,t=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=700
                ))

    st.plotly_chart(fig, use_container_width=True)

    # Export Section
    st.subheader("📊 Data Export")
    col1, col2 = st.columns(2)
    
    with col1:
        nodes_csv = filtered_entities.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Nodes CSV",
            data=nodes_csv,
            file_name="network_nodes.csv",
            mime="text/csv",
        )
        
    with col2:
        edges_csv = filtered_rels.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Edges CSV",
            data=edges_csv,
            file_name="network_edges.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    render()
