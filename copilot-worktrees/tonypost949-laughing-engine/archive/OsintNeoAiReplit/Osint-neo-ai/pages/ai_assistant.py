import streamlit as st
import os
from datetime import datetime

# Check if OpenAI is available (user's own key or Replit AI Integrations)
_AI_KEY = os.environ.get("OPENAI_API_KEY")
_REPLIT_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
_REPLIT_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_AVAILABLE = bool(_AI_KEY) or (bool(_REPLIT_BASE_URL) and bool(_REPLIT_KEY))

def get_openai_client():
    """Initialize OpenAI client using user's own key or Replit AI Integrations."""
    try:
        from openai import OpenAI
        # Prefer user's own OpenAI API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            return OpenAI(api_key=api_key)
        # Fallback to Replit AI Integrations
        base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
        api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
        if base_url and api_key:
            return OpenAI(api_key=api_key, base_url=base_url)
        return None
    except Exception:
        return None


def render():
    st.markdown("""
    <style>
    .main { background-color: #0a0e1a; color: #c8d8f0; }
    .stChatMessage {
        background-color: #0f1628;
        border: 1px solid #1e2d50;
        border-radius: 8px;
        margin: 0.5em 0;
    }
    .stChatMessage p { color: #c8d8f0; }
    .stChatMessage strong { color: #00d4ff; }
    .stChatMessage em { color: #ffd700; }
    .stChatMessage code {
        background-color: #1a2340;
        color: #00ff88;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .stChatMessage pre {
        background-color: #0a0e1a;
        border: 1px solid #1e2d50;
        border-radius: 6px;
        padding: 10px;
        overflow-x: auto;
    }
    .stChatMessage pre code { background-color: transparent; padding: 0; }
    .stChatMessage li { color: #c8d8f0; margin: 0.3em 0; }
    .stChatMessage a { color: #00d4ff; text-decoration: underline; }
    .stChatMessage blockquote {
        border-left: 3px solid #00d4ff;
        padding-left: 1em;
        margin: 0.5em 0;
        color: #8a9bb8;
    }
    .stChatMessage hr { border-color: #1e2d50; margin: 0.8em 0; }
    .stChatMessage h1, .stChatMessage h2, .stChatMessage h3 { color: #00d4ff !important; margin: 0.5em 0; }
    .stChatMessage h4, .stChatMessage h5, .stChatMessage h6 { color: #7b2fff !important; margin: 0.3em 0; }
    .stChatMessage table {
        border-collapse: collapse;
        width: 100%;
        margin: 0.5em 0;
    }
    .stChatMessage th, .stChatMessage td {
        border: 1px solid #1e2d50;
        padding: 6px 10px;
        text-align: left;
    }
    .stChatMessage th { background-color: #0f1628; color: #00d4ff; }
    .stChatMessage td { color: #c8d8f0; }
    .stChatMessage tr:nth-child(even) { background-color: #141d35; }
    .stChatMessage tr:nth-child(odd) { background-color: #0a0e1a; }
    .stChatMessage tr:hover { background-color: #1a2340; }
    .stChatInputContainer textarea {
        background-color: #141d35 !important;
        color: #e8f4ff !important;
        border: 1px solid #1e2d50 !important;
        font-family: 'Courier New', monospace !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🤖 AI OSINT Assistant")
    st.markdown("<p style='color:#5a7090;font-family:Courier New;'>AI-Powered investigative analysis and intelligence support.</p>", unsafe_allow_html=True)

    # Check if AI is available
    client = get_openai_client()
    if not client:
        st.warning("""
        ⚠️ **AI Not Connected**

        Your AI Assistant needs an OpenAI API key to function.
        
        **To connect:**
        1. Go to your Replit **Secrets** tab (🔒 icon in the left sidebar)
        2. Add a secret named `OPENAI_API_KEY` with your key (starts with `sk-...`)
        3. Refresh this page
        """, icon="🔑")
        st.info("Your API key is stored securely and never leaves this app.")
        return

    st.success("✅ AI Assistant Online — Ready to analyze your OSINT data.")

    # Initialize chat history
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = [
            {"role": "assistant", "content": "Welcome, investigator. I'm your AI OSINT assistant. I can analyze intelligence data, suggest investigative angles, interpret scan results, help with threat assessments, and answer OSINT-related questions. How can I assist your investigation today?"}
        ]

    # Display chat history
    for msg in st.session_state.ai_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    prompt = st.chat_input("Ask your AI assistant...")
    if prompt:
        # Add user message
        st.session_state.ai_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
                    # do not change this unless explicitly requested by the user
                    response = client.chat.completions.create(
                        model="gpt-5",
                        messages=[
                            {"role": "system", "content": "You are an expert OSINT (Open Source Intelligence) analyst and investigative assistant. You help investigators analyze data, identify patterns, suggest leads, interpret technical findings, and provide structured intelligence assessments. Be concise, professional, and actionable. Use markdown formatting for clarity."},
                            *[{"role": m["role"], "content": m["content"]} for m in st.session_state.ai_chat_history[-10:]]
                        ],
                        max_completion_tokens=8192
                    )
                    ai_reply = response.choices[0].message.content or ""
                    st.markdown(ai_reply)
                    st.session_state.ai_chat_history.append({"role": "assistant", "content": ai_reply})
                except Exception as e:
                    error_msg = f"⚠️ AI Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.ai_chat_history.append({"role": "assistant", "content": error_msg})

    # Quick action buttons
    st.markdown("<hr style='border-color:#1e2d50;margin:1.5em 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d4ff;font-family:Courier New;font-weight:bold;'>⚡ QUICK ACTIONS</p>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🎯 Analyze Threat", use_container_width=True):
            _quick_prompt("Analyze the current threat landscape based on the OSINT data. What are the highest-risk entities and why?")
    with col2:
        if st.button("📊 Summarize Data", use_container_width=True):
            _quick_prompt("Provide a comprehensive summary of all intelligence data in the system. Highlight key entities, relationships, and notable findings.")
    with col3:
        if st.button("🔍 Suggest Leads", use_container_width=True):
            _quick_prompt("Based on the OSINT data, suggest 3-5 investigative leads or angles to pursue next. Be specific and actionable.")
    with col4:
        if st.button("📝 Write Report", use_container_width=True):
            _quick_prompt("Draft a professional intelligence report based on the current data. Include executive summary, key findings, and recommendations.")


def _quick_prompt(prompt_text):
    """Helper to inject a quick-action prompt into the chat."""
    st.session_state.ai_chat_history.append({"role": "user", "content": prompt_text})
    st.rerun()
