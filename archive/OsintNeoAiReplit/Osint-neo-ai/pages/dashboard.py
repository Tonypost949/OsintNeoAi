import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import sqlite3
import streamlit.components.v1 as components
from utils.database import get_stats, get_all_entities, get_all_events

DB_PATH = "data/osint_master.db"


@st.cache_data(ttl=60, show_spinner=False)
def _file_chart_data():
    conn = sqlite3.connect(DB_PATH)
    risk_df = pd.read_sql_query(
        "SELECT risk_flag as 'Risk Level', COUNT(*) as Count FROM file_scan_results GROUP BY risk_flag ORDER BY Count DESC",
        conn,
    )
    cat_df = pd.read_sql_query(
        "SELECT category, COUNT(*) as Count FROM file_scan_results GROUP BY category ORDER BY Count DESC LIMIT 10",
        conn,
    )
    conn.close()
    return risk_df, cat_df


@st.cache_data(ttl=300, show_spinner=False)
def _build_map_html(entity_tuples):
    """Build a Folium map and return static HTML — no reruns triggered."""
    m = folium.Map(location=[30, -10], zoom_start=2, tiles="CartoDB dark_matter")
    color_map = {"High": "red", "Medium": "orange", "Low": "green", "Unknown": "blue"}
    for label, risk, geo, etype, source in entity_tuples:
        try:
            parts = geo.replace(" ", "").split(",")
            if len(parts) == 2:
                lat, lon = float(parts[0]), float(parts[1])
                color = color_map.get(risk, "blue")
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=12,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.8,
                    tooltip=f"{label} ({risk})",
                    popup=f"<b>{label}</b><br>Type: {etype}<br>Risk: {risk}<br>Source: {source}",
                ).add_to(m)
        except Exception:
            pass
    return m.get_root().render()



def render():
    st.markdown("## 🌐 Global Intelligence Dashboard")

    stats = get_stats()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📌 Entities", stats["entities"])
    col2.metric("🔗 Relationships", stats["relationships"])
    col3.metric("📅 Events", stats["events"])
    col4.metric("🔴 High Risk", stats["high_risk"])
    col5.metric("📁 File Scans", stats["file_scans"])

    st.divider()

    entities = get_all_entities()

    entity_tuples = tuple(
        (e.get("label", ""), e.get("risk_level", "Unknown"),
         e.get("geo_location", ""), e.get("type", ""), e.get("source", ""))
        for e in entities
    )

    col_map, col_chart = st.columns([2, 1])

    with col_map:
        st.markdown("### 🗺️ Entity Geolocation Map")
        map_html = _build_map_html(entity_tuples)
        components.html(map_html, height=420, scrolling=False)

    with col_chart:
        st.markdown("### 📊 File Risk Distribution")
        risk_df, cat_df = _file_chart_data()

        if not risk_df.empty:
            color_map_px = {"High": "#E74C3C", "Medium": "#F39C12", "Low": "#27AE60", "Unknown": "#5A7090"}
            fig = px.pie(
                risk_df, values="Count", names="Risk Level",
                color="Risk Level", color_discrete_map=color_map_px,
                hole=0.5
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#C8D8F0",
                legend=dict(font=dict(color="#C8D8F0")),
                margin=dict(t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🗂️ File Categories")
        if not cat_df.empty:
            fig2 = px.bar(cat_df, x="Count", y="category", orientation="h",
                          color="Count", color_continuous_scale="teal")
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#C8D8F0",
                yaxis_title="",
                margin=dict(t=10, b=10, l=10),
                showlegend=False,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    st.markdown("### 🕒 Recent Events Timeline")
    events = get_all_events()
    if events:
        df_ev = pd.DataFrame(events[:10])
        df_ev = df_ev[["event_id", "timestamp", "event_type", "location", "entities_involved", "source"]]
        df_ev.columns = ["Event ID", "Date", "Type", "Location", "Entities", "Source"]
        st.dataframe(df_ev, use_container_width=True, hide_index=True)
