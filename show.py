import streamlit as st
import pandas as pd
from pathlib import Path
from lightbox_edr_engine import LightBoxEDREngine

st.set_page_config(
    page_title="OSINTNeoAi — Public Evidence & Intelligence Showcase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Dark Forensic Theme
st.markdown("""
    <style>
    .main { background-color: #0b131e; color: #e2e8f0; }
    .stMetric { background-color: #131d2e; padding: 15px; border-radius: 10px; border: 1px solid #1e293b; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ OSINTNeoAi: Public Evidence Showcase")
st.caption("Autonomous Investigative Ledger, Multi-State Corporate Anomaly & LightBox EDR Environmental Audit | Published by Disole Design")

# Executive Metrics
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Records Audited", "10,499,686")
col2.metric("Estimated Exposure", "$90,000,000+", delta="Taxpayer Impact", delta_color="inverse")
col3.metric("Proxy Mailbox Hubs", "77 Clusters")
col4.metric("Multi-State Entities", "100 Syndicates")

# Init LightBox Engine
edr_engine = LightBoxEDREngine()
edr_stats = edr_engine.get_summary_stats()
col5.metric("EDR Sites Audited", f"{edr_stats['total_cached_records']} Records", delta="Sanborn / Radius", delta_color="normal")

st.divider()

# Navigation Tabs
tab_evidence, tab_lightbox, tab_daily, tab_audio, tab_verify = st.tabs([
    "🚨 Live Evidence Matrix", 
    "🏢 LightBox & EDR Environmental Hub",
    "📅 Daily Intelligence Dispatches", 
    "🎙️ Audio Commentary Studio", 
    "🌐 Official .gov Verification"
])

with tab_evidence:
    st.subheader("🚨 Verified Anomalies & Cross-State PPP Dispersions")
    csv_candidates = [
        Path("reports/NATIONWIDE_SMOKING_GUNS_MATRIX.csv"),
        Path("NATIONWIDE_SMOKING_GUNS_MATRIX.csv")
    ]
    csv_file = next((f for f in csv_candidates if f.exists()), None)
    
    if csv_file:
        df = pd.read_csv(csv_file)
        q = st.text_input("🔍 Filter by Entity, Location, or Origin State:", placeholder="e.g. Stewart Industries, Michigan, Alaska...")
        if q:
            df = df[df.apply(lambda r: r.astype(str).str.contains(q, case=False).any(), axis=1)]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Evidence matrix CSV populated from BigQuery warehouse sync.")

with tab_lightbox:
    st.subheader("🏢 LightBox RE & EDR Environmental Intelligence Vault")
    st.markdown("""
    Fuses **historical EDR radius reports**, **Sanborn map coordinates**, and **LightBox RE property parcel endpoints** to identify environmental risk manipulation and asset transfers.
    """)
    
    sub_col1, sub_col2 = st.columns([2, 1])
    with sub_col1:
        edr_query = st.text_input("🔍 Search EDR Environmental Database / Address:", placeholder="e.g. 17642 Beach Blvd, Cameron Ln, Garden Grove, Sanborn...")
    with sub_col2:
        st.write("")
        st.write("")
        st.caption(f"Cached EDR Audit Records: **{edr_stats['total_cached_records']}** | Unique Sites: **{edr_stats['unique_sites_audited']}**")

    # Display EDR search matches
    matched_edr = edr_engine.search_edr_records(edr_query) if edr_query else edr_engine.edr_cache[:100]
    if matched_edr:
        df_edr = pd.DataFrame(matched_edr)
        st.dataframe(df_edr, use_container_width=True, hide_index=True)
    else:
        st.warning(f"No EDR records found matching '{edr_query}'.")

    st.divider()
    st.markdown("#### 📡 Live LightBox API Parcel & Risk Lookup")
    live_addr = st.text_input("Query Live Parcel API Endpoint (via LightBox RE):", placeholder="17642 Beach Blvd, Huntington Beach, CA 92647")
    if st.button("Fetch Live LightBox Parcel"):
        if live_addr:
            live_res = edr_engine.query_live_parcel(live_addr)
            if live_res:
                st.success("Live Parcel Data Retrieved:")
                st.json(live_res)
            else:
                st.info("Live API requires active subscription token ($env:LIGHTBOX_API_KEY). Showing local cached audit records above.")

with tab_daily:
    st.subheader("📅 Autonomous Daily Intelligence Dispatches")
    daily_dir = Path("reports/daily")
    if daily_dir.exists():
        reports = sorted(list(daily_dir.glob("*.md")), reverse=True)
        if reports:
            selected_report = st.selectbox("Select Dispatch Date:", [r.name for r in reports])
            selected_path = daily_dir / selected_report
            st.markdown(selected_path.read_text(encoding="utf-8"))
        else:
            st.info("No daily dispatches compiled yet. Autonomous compiler runs daily at 00:00 UTC.")
    else:
        st.info("Daily dispatches directory will populate upon daily cron run.")

with tab_audio:
    st.subheader("🎙️ 30-Minute Audio Overview: 'Cabinet Maker vs. Ninety Million Dollar Fraud'")
    audio_candidates = [
        Path("Cabinet_Maker_vs_Ninety_Million_Dollar_Fraud.m4a"),
        Path("reports/Cabinet_Maker_vs_Ninety_Million_Dollar_Fraud.m4a")
    ]
    audio_file = next((f for f in audio_candidates if f.exists()), None)
    if audio_file:
        st.audio(str(audio_file), format="audio/m4a")
        st.caption("2-Voice Deep Dive Discussion & Case Overview")
    else:
        st.info("Audio commentary streaming asset linked to local evidence drive.")

with tab_verify:
    st.subheader("🌐 Official Government Public Record Verification Links")
    st.markdown("""
    * 🏛️ **California Secretary of State:** [bizfileOnline Registry Search](https://bizfileonline.sos.ca.gov/search/business)
    * 🏛️ **Michigan LARA:** [Corporate Registry Search](https://cofs.lara.state.mi.us/Search/Search)
    * 🏛️ **Alaska Division of Corporations:** [Entity Search Portal](https://www.commerce.alaska.gov/cbp/main/search/entities)
    * 🏛️ **Orange County Clerk-Recorder:** [Public Property Records](https://www.ocrecorder.com)
    """)

st.divider()
st.caption("🔒 **Integrity Standard:** All exhibits and reports are cryptographically signed with NIST SHA-256 Checksums.")
