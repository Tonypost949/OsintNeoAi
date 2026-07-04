import streamlit as st
import pandas as pd
import uuid
import sys

# Ensure stdout handles special characters
sys.stdout.reconfigure(encoding='utf-8')

from agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

# -----------------------------------------------------------------------------
# PAGE SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NWORICO Data Engine",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# -----------------------------------------------------------------------------
# CSS DESIGN SYSTEM
# -----------------------------------------------------------------------------
css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,700;1,300&family=Inter:wght@400;500;600;700&display=swap');

:root {{
    /* Deep slate dark mode, off-white warm newspaper light mode */
    --bg: {'#0a0a0a' if IS_DARK else '#fdfbf7'};
    --bg-subtle: {'#121212' if IS_DARK else '#f4f2eb'};
    --card: {'#121212' if IS_DARK else '#ffffff'};
    --card-hover: {'#1a1a1a' if IS_DARK else '#fdfbf7'};
    --border: {'#262626' if IS_DARK else '#e5e5e5'};
    --border-subtle: {'#1f1f1f' if IS_DARK else '#f0f0f0'};
    --text: {'#ededed' if IS_DARK else '#1a1a1a'};
    --text-muted: {'#a3a3a3' if IS_DARK else '#52525b'};
    --text-dim: {'#737373' if IS_DARK else '#a1a1aa'};
    --accent: {'#3b82f6' if IS_DARK else '#0f172a'};
    --accent-muted: {'#2563eb' if IS_DARK else '#334155'};
    --green: {'#22c55e' if IS_DARK else '#16a34a'};
    --green-muted: {'rgba(34,197,94,0.12)' if IS_DARK else 'rgba(22,163,74,0.08)'};
    --red: {'#ef4444' if IS_DARK else '#dc2626'};
    --red-muted: {'rgba(239,68,68,0.12)' if IS_DARK else 'rgba(220,38,38,0.08)'};
    --amber: {'#f59e0b' if IS_DARK else '#d97706'};
    --amber-muted: {'rgba(245,158,11,0.12)' if IS_DARK else 'rgba(217,119,6,0.08)'};
    --shadow: {'none' if IS_DARK else '0 2px 4px rgba(0,0,0,0.02), 0 1px 2px rgba(0,0,0,0.01)'};
    --radius: {'10px' if IS_DARK else '2px'};
}}

/* Hide Streamlit chrome */
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
div[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: {'"Inter", -apple-system, sans-serif' if IS_DARK else '"Merriweather", Georgia, serif'} !important;
}}
.block-container {{
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1360px !important;
}}

.metric-card {{ background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem 1.4rem; box-shadow: var(--shadow); }}
.metric-label {{ font-family: "Inter", sans-serif; font-size: 0.78rem; color: var(--text-muted); font-weight: {'500' if IS_DARK else '700'}; text-transform: uppercase; letter-spacing: 0.05em; }}
.metric-value {{ font-family: "Inter", sans-serif; font-size: 1.75rem; font-weight: {'600' if IS_DARK else '300'}; color: var(--text); letter-spacing: -0.03em; margin-top: 0.3rem; }}
.metric-delta {{ font-family: "Inter", sans-serif; font-size: 0.75rem; font-weight: 500; margin-top: 0.4rem; padding: 2px 8px; border-radius: 6px; display: inline-flex; align-items: center; gap: 3px; }}
.delta-up {{ color: var(--green); background: var(--green-muted); }}
.delta-down {{ color: var(--red); background: var(--red-muted); }}
.delta-warn {{ color: var(--amber); background: var(--amber-muted); }}

.brand {{ font-family: {'"Inter", sans-serif' if IS_DARK else '"Merriweather", serif'}; font-size: {'1.2rem' if IS_DARK else '1.5rem'}; font-weight: {'700' if IS_DARK else '300'}; color: var(--text); display: flex; align-items: center; gap: 8px; }}
.brand-name {{ letter-spacing: -0.02em; }}

[data-testid="stHorizontalBlock"] {{ gap: 1.25rem !important; }}

/* Chat UI Overrides */
[data-testid="chatAvatarIcon-user"] {{ background-color: var(--accent) !important; }}
[data-testid="chatAvatarIcon-assistant"] {{ background-color: var(--border) !important; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

def metric_card(label, value, delta=None, delta_type="up"):
    cls = f"delta-{delta_type}"
    arrow = "↑" if delta_type == "up" else ("↓" if delta_type == "down" else "→")
    delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BACKEND STATE
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
if "runner" not in st.session_state:
    st.session_state.runner = Runner(
        app_name="nworico_dashboard",
        agent=root_agent,
        session_service=InMemorySessionService(),
        auto_create_session=True
    )

# -----------------------------------------------------------------------------
# APP LAYOUT
# -----------------------------------------------------------------------------
head_left, head_right = st.columns([8, 1])
with head_left:
    st.markdown("""
    <div class="brand">
        ◆ <span class="brand-name">NWORICO Data Engine</span>
    </div>
    <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 5px; margin-bottom: 20px;">
        OSINTNeoAi Target Intelligence Matrix • Project: project-743aab84-f9a5-4ec7-954
    </div>
    """, unsafe_allow_html=True)
with head_right:
    theme_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True)

# Dashboards / KPIs
c1, c2, c3 = st.columns(3)
with c1: metric_card("Untracked CA Funds", "$24,000,000,000", delta="State Audit 2023-102.1", delta_type="warn")
with c2: metric_card("Huntington Extracted Leakage", "$1,100,000.00", delta="Target: Mercy House", delta_type="down")
with c3: metric_card("Active Proxy Nodes", "3 States", delta="CA, AZ, VA", delta_type="up")

st.markdown("<br>", unsafe_allow_html=True)

tab_chat, tab_map, tab_tools = st.tabs(["Agent Terminal", "50-State GIS Map", "System Capabilities"])

with tab_chat:
    # -----------------------------------------------------------------------------
    # CHAT INTERFACE
    # -----------------------------------------------------------------------------
    st.markdown("### Agent Terminal")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Query OSINTNeoAi (e.g. 'Analyze Mercy House')"):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            thought_placeholder = st.empty()
            response_placeholder = st.empty()
            
            full_response = ""
            full_thoughts = ""
            
            new_msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
            
            try:
                # Sync generator handles streaming seamlessly
                for event in st.session_state.runner.run(
                    user_id="user1", 
                    session_id=st.session_state.session_id, 
                    new_message=new_msg
                ):
                    if hasattr(event, 'output') and event.output:
                        # 'output' often contains thoughts or intermediate steps
                        full_thoughts += event.output
                        thought_placeholder.info(f"**Agent Thought Process:**\n```\n{full_thoughts}\n```")
                        
                    if hasattr(event, 'content') and event.content:
                        for part in event.content.parts:
                            if part.text:
                                full_response += part.text
                                response_placeholder.markdown(full_response + "▌")
                                
            except Exception as e:
                full_response += f"\n\n**Error:** `{str(e)}`"
                
            response_placeholder.markdown(full_response)
            
            # Save to state once done
            st.session_state.messages.append({"role": "assistant", "content": full_response})

with tab_map:
    st.markdown("### 50-State Environmental & Corporate GIS Matrix")
    st.info("Loading geographical proxy coordinates from BigQuery: `project-743aab84-f9a5-4ec7-954.national_audits.environmental_site_assessments`...")
    # Base coordinate map for the Huntington Beach core template
    map_data = pd.DataFrame({'lat': [33.684], 'lon': [-117.994], 'site': ['Huntington Beach Nav Center']})
    st.map(map_data, zoom=10, use_container_width=True)

with tab_tools:
    st.markdown("### Integrated Data Streams & Agent Tools")
    st.markdown("""
    1. **State-level Performance Audits:** Tracks CA Joint Legislative Audit 2023-102.1 ($24B gap).
    2. **HUD PIT Counts:** Cross-references sheltered vs unsheltered demographics.
    3. **CoC Continuum of Care Funding:** Maps exact HUD award amounts per operational sector.
    4. **Non-Profiteers Corporate Shell Index:** Tracks zero-count entities and `cms_billing_codes`.
    5. **Environmental Site Assessments (GeoTracker):** Maps physical footprints against toxic limits.
    
    **Engineered Tools:**
    - `project-743aab84-f9a5-4ec7-954.national_audits.calculate_fund_leakage(total_funds, reported_expenditure)` Mathematical UDF
    - Anti-Duplication Single-Array SQL Cross-referencing Protocol
    """)
