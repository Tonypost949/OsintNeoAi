import streamlit as st
from utils.database import init_db

st.set_page_config(
    page_title="OSINT AI Neo",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom dark theme CSS matching the OSINT Neo AI design
st.markdown("""
<style>
  :root {
    --bg: #0a0e1a;
    --panel: #0f1628;
    --panel2: #141d35;
    --border: #1e2d50;
    --accent: #00d4ff;
    --accent2: #7b2fff;
    --green: #00ff88;
    --yellow: #ffd700;
    --red: #ff4444;
    --text: #c8d8f0;
    --text-dim: #5a7090;
    --text-bright: #e8f4ff;
  }

  .stApp { background-color: #0a0e1a; }
  .stSidebar { background-color: #0f1628; border-right: 1px solid #1e2d50; }
  .stSidebar [data-testid="stSidebarContent"] { background-color: #0f1628; }

  h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New', monospace; }
  p, label, .stMarkdown { color: #c8d8f0; }

  .stMetric { background: #141d35; border: 1px solid #1e2d50; border-radius: 8px; padding: 12px; }
  .stMetric label { color: #5a7090 !important; font-size: 0.78rem; }
  .stMetric [data-testid="metric-container"] { color: #00d4ff; }

  .stDataFrame { border: 1px solid #1e2d50; border-radius: 6px; }
  .stDataFrame thead th { background: #0f1628 !important; color: #00d4ff !important; }

  .stButton > button {
    background: transparent;
    border: 1px solid #00d4ff;
    color: #00d4ff;
    font-family: 'Courier New', monospace;
    font-weight: bold;
    letter-spacing: 0.05em;
    transition: all 0.15s;
  }
  .stButton > button:hover {
    background: rgba(0,212,255,0.1);
    box-shadow: 0 0 12px rgba(0,212,255,0.4);
  }
  .stButton > button[kind="primary"] {
    background: #00d4ff;
    color: #000;
  }
  .stButton > button[kind="primary"]:hover {
    background: #00b8e0;
    box-shadow: 0 0 18px rgba(0,212,255,0.6);
  }

  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div {
    background: #141d35 !important;
    border: 1px solid #1e2d50 !important;
    color: #e8f4ff !important;
    font-family: 'Courier New', monospace;
  }

  .stTabs [data-baseweb="tab-list"] { background: #0f1628; border-bottom: 1px solid #1e2d50; }
  .stTabs [data-baseweb="tab"] { color: #5a7090; font-family: 'Courier New', monospace; }
  .stTabs [aria-selected="true"] { color: #00d4ff !important; border-bottom: 2px solid #00d4ff; }

  .stExpander { border: 1px solid #1e2d50; background: #0f1628; border-radius: 6px; }
  .stExpander > details > summary { color: #00d4ff; }

  .stAlert { border-radius: 6px; font-family: 'Courier New', monospace; }
  [data-testid="stSidebarNav"] { display: none; }

  .sidebar-logo {
    padding: 1em;
    border-bottom: 1px solid #1e2d50;
    margin-bottom: 0.5em;
  }
  .sidebar-logo .title { color: #00d4ff; font-size: 1.2rem; font-weight: bold; letter-spacing: 0.2em; font-family: 'Courier New', monospace; }
  .sidebar-logo .sub { color: #5a7090; font-size: 0.7rem; letter-spacing: 0.15em; }
  .status-line { display: flex; align-items: center; gap: 0.4em; color: #00ff88; font-size: 0.72rem; margin-top: 0.5em; font-family: 'Courier New', monospace; }
  .dot { width: 6px; height: 6px; background: #00ff88; border-radius: 50%; display: inline-block; box-shadow: 0 0 6px #00ff88; }
</style>
""", unsafe_allow_html=True)

# Initialize DB on startup
init_db()

# Sidebar branding + navigation
st.sidebar.markdown("""
<div class='sidebar-logo'>
  <div class='title'>🛡️ OSINT AI NEO</div>
  <div class='sub'>INVESTIGATIVE INTELLIGENCE PLATFORM</div>
  <div class='status-line'><span class='dot'></span> SYSTEM ONLINE</div>
</div>
""", unsafe_allow_html=True)

PAGES = {
    "🌐 Dashboard":            "dashboard",
    "🎯 Target Enumeration":   "target_enum",
    "📊 Master Sheet":         "master_sheet",
    "📁 File & Folder Scanner":"file_scanner",
    "🧠 NLP Analysis":         "nlp_analysis",
    "📱 Social Media":         "social_media",
    "🏛️ NP — Nonprofit Intel": "nonprofit",
    # ── New parallel-built features ──────────────────────────────────────
    "🔍 Advanced Search":      "search",
    "👤 Person Deep-Dive":     "deep_dive",
    "🕸️ Network Graph":        "network_graph",
    "📄 Report Generator":     "report_gen",
    "📡 Live Feed Monitor":    "live_feed",
    "🎯 Threat Scoring":       "threat_score",
    "🤖 AI Assistant":         "ai_assistant",
    "🏘️ Real Estate Analyzer": "real_estate",
}

page = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")

st.sidebar.divider()
st.sidebar.markdown("""
<div style='font-size:0.7rem;color:#5a7090;font-family:Courier New;padding:0 0.5em;'>
<b style='color:#00d4ff'>CAPABILITY INDEX</b><br><br>
🔴 Target Scan<br>
🔵 Entity Graph<br>
🟢 File EXIF Extract<br>
🟡 NLP Analysis<br>
🟣 Social OSINT<br>
⚪ Master Export<br>
🔍 Global Search<br>
👤 Deep Dossier<br>
🕸️ Network Graph<br>
📄 PDF Reports<br>
📡 Live Feed<br>
🎯 Threat Score<br>
🤖 AI Assistant<br>
🏘️ Real Estate
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.markdown("<div style='font-size:0.75rem;color:#00d4ff;font-family:Courier New;padding:0 0.5em 0.3em;'>📱 ANDROID SCANNER</div>", unsafe_allow_html=True)
try:
    with open("phone_scanner.py", "rb") as _f:
        st.sidebar.download_button(
            label="⬇️ Download phone_scanner.py",
            data=_f,
            file_name="phone_scanner.py",
            mime="text/plain",
            use_container_width=True,
        )
except Exception:
    pass
st.sidebar.caption("OSINT AI Neo v2.0 | Build 2024")

# Route to page
selected = PAGES[page]

if selected == "dashboard":
    from pages.dashboard import render
    render()
elif selected == "target_enum":
    from pages.target_enum import render
    render()
elif selected == "master_sheet":
    from pages.master_sheet import render
    render()
elif selected == "file_scanner":
    from pages.file_scanner_page import render
    render()
elif selected == "nlp_analysis":
    from pages.nlp_analysis import render
    render()
elif selected == "social_media":
    from pages.social_media import render
    render()
elif selected == "nonprofit":
    from pages.nonprofit import render
    render()
elif selected == "search":
    from pages.search import render
    render()
elif selected == "deep_dive":
    from pages.deep_dive import render
    render()
elif selected == "network_graph":
    from pages.network_graph import render
    render()
elif selected == "report_gen":
    from pages.report_gen import render
    render()
elif selected == "live_feed":
    from pages.live_feed import render
    render()
elif selected == "threat_score":
    from pages.threat_score import render
    render()
elif selected == "ai_assistant":
    from pages.ai_assistant import render
    render()
elif selected == "real_estate":
    from pages.real_estate import render
    render()
