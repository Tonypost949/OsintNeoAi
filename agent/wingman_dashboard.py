import streamlit as st
import pandas as pd
from google.cloud import bigquery
import os

st.set_page_config(
    page_title="OSINTNeoAi Mobile",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# CSS injection
css = f"""
<style>
:root {{
    --bg: {'#09090b' if IS_DARK else '#ffffff'};
    --bg-subtle: {'#0c0c0f' if IS_DARK else '#f9fafb'};
    --card: {'#0c0c0f' if IS_DARK else '#ffffff'};
    --card-hover: {'#131316' if IS_DARK else '#f4f4f5'};
    --border: {'#1e1e24' if IS_DARK else '#e4e4e7'};
    --border-subtle: {'#16161a' if IS_DARK else '#f0f0f2'};
    --text: {'#fafafa' if IS_DARK else '#09090b'};
    --text-muted: #71717a;
    --text-dim: {'#52525b' if IS_DARK else '#a1a1aa'};
    --accent: #2563eb;
    --green: {'#22c55e' if IS_DARK else '#16a34a'};
    --red: {'#ef4444' if IS_DARK else '#dc2626'};
    --shadow: {'none' if IS_DARK else '0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)'};
    --radius: 10px;
}}
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
div[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}}
.block-container {{
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1360px !important;
}}
.metric-card {{ background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem 1.4rem; box-shadow: var(--shadow); }}
.metric-label {{ font-size: 0.78rem; color: var(--text-muted); font-weight: 500; }}
.metric-value {{ font-size: 1.75rem; font-weight: 700; color: var(--text); letter-spacing: -0.03em; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Brand / Logo Header
head_left, head_right = st.columns([8, 1])
with head_left:
    st.markdown("""
    <div style="font-size:1.5rem; font-weight:bold;">
        🦅 OSINTNeoAi Mobile
    </div>
    """, unsafe_allow_html=True)
with head_right:
    theme_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True)

@st.cache_data(ttl=600)
def load_data(query):
    client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
    return client.query(query).to_dataframe()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Cyber Recon", "Regional LLCs", "I-Soon Telemetry", "OSINTNeoAi Chat"])

with tab1:
    st.subheader("RICO Operations Overview")
    
    try:
        recon_count = load_data("SELECT COUNT(*) as c FROM ppp_rico.city_cyber_recon")['c'][0]
        llc_count = load_data("SELECT COUNT(*) as c FROM ppp_rico.regional_llcs")['c'][0]
        match_count = load_data("SELECT COUNT(*) as c FROM ppp_rico.trafficking_matches")['c'][0]
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="metric-label">Exposed Endpoints</div><div class="metric-value">{recon_count}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="metric-label">Regional LLCs Found</div><div class="metric-value">{llc_count}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><div class="metric-label">Trafficking Matches</div><div class="metric-value">{match_count}</div></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading metrics: {e}")

with tab2:
    st.subheader("City Cyber Recon")
    st.write("Exposed administrative and backup paths found on city and police domains.")
    try:
        df_recon = load_data("SELECT * FROM ppp_rico.city_cyber_recon LIMIT 500")
        st.dataframe(df_recon, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading recon data: {e}")

with tab3:
    st.subheader("Regional LLCs")
    try:
        df_llcs = load_data("SELECT * FROM ppp_rico.regional_llcs")
        st.dataframe(df_llcs, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading LLC data: {e}")

with tab4:
    st.subheader("I-Soon Telecom Telemetry")
    st.write("Ingested cellular telemetry datasets from the Sichuan I-Soon (Anxun) leaks.")
    
    dataset_choice = st.selectbox(
        "Select Telemetry Dataset",
        ["Beeline CRM (Subscriber Profiles)", "Beeline LBS (Location Logs)", "Beeline CDR (Call Records)", "IDNet Database"]
    )
    
    table_mapping = {
        "Beeline CRM (Subscriber Profiles)": "ppp_rico.beeline_crm",
        "Beeline LBS (Location Logs)": "ppp_rico.beeline_lbs",
        "Beeline CDR (Call Records)": "ppp_rico.beeline_cdr",
        "IDNet Database": "ppp_rico.idnet"
    }
    
    try:
        selected_table = table_mapping[dataset_choice]
        df_telemetry = load_data(f"SELECT * FROM {selected_table} LIMIT 250")
        st.dataframe(df_telemetry, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading telemetry: {e}")

with tab5:
    st.subheader("OSINTNeoAi Assistant & Query Runner")
    
    col_chat, col_sql = st.columns([1, 1])
    
    with col_chat:
        st.markdown("### 💬 AI Assistant")
        st.write("Ask questions or generate SQL queries.")
        
        # Initialize Gemini client
        try:
            from google import genai
            genai_client = genai.Client()
        except Exception as e:
            st.error(f"Error loading Gemini SDK: {e}")
            genai_client = None

        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "prev_interaction_id" not in st.session_state:
            st.session_state.prev_interaction_id = None

        # Container for chat messages with fixed height using custom CSS if needed
        chat_container = st.container(height=400)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Ask OSINTNeoAi about the RICO data..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            with chat_container:
                with st.chat_message("assistant"):
                    if genai_client:
                        with st.spinner("OSINTNeoAi is thinking..."):
                            try:
                                system_instruction = (
                                    "You are OSINTNeoAi, an OSINT and RICO investigation assistant. "
                                    "You are connected to a BigQuery dataset `ppp_rico` in project `project-743aab84-f9a5-4ec7-954`. "
                                    "The user is investigating a network involving Mercy House shelters, Medi-Cal billing fraud, and PPP fraud. "
                                    "The tables in the dataset are:\n"
                                    "1. `city_cyber_recon`: Contains exposed administrative paths found on city/police domains.\n"
                                    "2. `regional_llcs`: Contains regional LLCs mapped to the investigation.\n"
                                    "3. `trafficking_matches`: Matches of targets Carmen Luege, Victor Nunez, Paul Barnes.\n\n"
                                    "Answer the user's questions about the investigation using this context. "
                                    "CRITICAL: If they ask for data or queries, write SQL queries they can run on these tables. Do NOT make up or simulate query results; tell the user to copy the query and paste it into the SQL Query Runner on the right to get real results."
                                )
                                
                                kwargs = {
                                    "model": "gemini-3.5-flash",
                                    "input": prompt,
                                    "system_instruction": system_instruction
                                }
                                if st.session_state.prev_interaction_id:
                                    kwargs["previous_interaction_id"] = st.session_state.prev_interaction_id

                                interaction = genai_client.interactions.create(**kwargs)
                                st.session_state.prev_interaction_id = interaction.id
                                response = interaction.output_text or "No response received."
                                # Log to file
                                try:
                                    log_path = "chatbot_findings_log.md"
                                    with open(log_path, "a", encoding="utf-8") as lf:
                                        lf.write(f"## User Query\n{prompt}\n\n## Assistant Response\n{response}\n\n---\n\n")
                                except Exception:
                                    pass
                            except Exception as e:
                                response = f"Error calling Gemini API: {e}"
                    else:
                        response = "Gemini client is not initialized. Please verify your SDK and API Key configuration."

                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

    with col_sql:
        st.markdown("### 🔍 Live BigQuery SQL Runner")
        st.write("Run real-time SQL queries against the `project-743aab84-f9a5-4ec7-954` project.")
        
        default_query = "SELECT * FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.trafficking_matches` LIMIT 10"
        query_input = st.text_area("Enter SQL Query:", value=default_query, height=150)
        
        if st.button("Run SQL Query", use_container_width=True):
            with st.spinner("Executing query on BigQuery..."):
                try:
                    df_res = load_data(query_input)
                    st.success(f"Success! Returned {len(df_res)} rows.")
                    st.dataframe(df_res, use_container_width=True)
                except Exception as e:
                    st.error(f"SQL Execution Error: {e}")

