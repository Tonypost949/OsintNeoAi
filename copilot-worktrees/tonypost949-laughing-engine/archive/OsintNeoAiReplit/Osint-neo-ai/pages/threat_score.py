import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from utils.threat_scorer import score_all_entities, apply_scores_to_db

DB_PATH = "data/osint_master.db"

def render():
    st.markdown("""
    <style>
    .main {
        background-color: #0a0e1a;
        color: #c8d8f0;
    }
    .stButton>button {
        background-color: #0f1628;
        color: #00d4ff;
        border: 1px solid #1e2d50;
    }
    .stDataFrame {
        border: 1px solid #1e2d50;
    }
    .badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-high { background-color: #ff4b4b; color: white; }
    .badge-medium { background-color: #ffaa00; color: black; }
    .badge-low { background-color: #00ff88; color: black; }
    .badge-unknown { background-color: #888888; color: white; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🧠 AI Threat Scoring")
    st.write("Pattern-based entity threat analysis using relationships, notes, and file scan intelligence.")

    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🚀 Run Threat Analysis"):
            with st.spinner("Analyzing entities..."):
                results = score_all_entities(DB_PATH)
                st.session_state.analysis_results = results
                st.success(f"Analyzed {len(results)} entities.")

    with col2:
        if st.session_state.analysis_results:
            changed_only = [r for r in st.session_state.analysis_results if r["level"] != r["old_level"]]
            if st.button(f"📥 Apply Upgrades ({len(changed_only)} entities)"):
                upgraded = apply_scores_to_db(DB_PATH, st.session_state.analysis_results)
                st.success(f"Successfully upgraded {upgraded} entities in database.")
                # Refresh analysis after applying
                st.session_state.analysis_results = score_all_entities(DB_PATH)

    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Filters
        st.divider()
        show_changed = st.checkbox("Show only level changes", value=False)
        
        display_results = results
        if show_changed:
            display_results = [r for r in results if r["level"] != r["old_level"]]

        if not display_results:
            st.info("No entities match the current filter.")
        else:
            # Stats/Chart
            df = pd.DataFrame(display_results)
            
            fig = px.histogram(df, x="score", nbins=20, title="Threat Score Distribution",
                               color_discrete_sequence=['#00d4ff'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#c8d8f0',
                xaxis_title="Score (0-100)",
                yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Results Table
            for res in display_results:
                with st.container():
                    c1, c2, c3 = st.columns([2, 3, 1])
                    
                    with c1:
                        st.markdown(f"**{res['label']}**")
                        st.caption(f"{res['type']} | {res['entity_id']}")
                        
                    with c2:
                        score = res['score']
                        bar_color = "green"
                        if score >= 80: bar_color = "red"
                        elif score >= 50: bar_color = "orange"
                        elif score >= 20: bar_color = "yellow"
                        
                        st.progress(score / 100.0)
                        factors = res['factors'][:3]
                        if factors:
                            st.caption(f"Top factors: {', '.join(factors)}")
                        else:
                            st.caption("No significant threat factors detected.")

                    with c3:
                        level = res['level']
                        badge_class = f"badge-{level.lower()}"
                        st.markdown(f'<div class="badge {badge_class}">{level}</div>', unsafe_allow_html=True)
                        if res['level'] != res['old_level']:
                            st.caption(f"Prev: {res['old_level']}")
                    
                    st.divider()

if __name__ == "__main__":
    render()
