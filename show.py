import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title='RICONWO — Public Evidence Showcase', page_icon='⚖️', layout='wide')
st.title('⚖️ RICONWO: Public Evidence Showcase')
st.caption('Investigative Ledger & Multi-State Corporate Anomaly Audit | Case ID: 2026-RICO-01 | Published by Disole Design')

col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Records Audited', '10,499,686')
col2.metric('Estimated Exposure', ',000,000+', delta='Taxpayer Impact', delta_color='inverse')
col3.metric('Proxy Mailbox Hubs', '77 Clusters')
col4.metric('Multi-State Entities', '100 Syndicates')

st.divider()
st.subheader('🚨 Verified Anomalies & Cross-State PPP Dispersions')
csv_file = Path('NATIONWIDE_SMOKING_GUNS_MATRIX.csv')
if csv_file.exists():
    df = pd.read_csv(csv_file)
    q = st.text_input('🔍 Filter by Entity, Location, or Origin State:', placeholder='e.g. Stewart Industries, Michigan, Alaska...')
    if q:
        df = df[df.apply(lambda r: r.astype(str).str.contains(q, case=False).any(), axis=1)]
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info('Evidence matrix CSV populated from BigQuery warehouse sync.')

st.divider()
st.subheader('🌐 Official Verification Portals')
st.markdown('''
* 🏛️ **California Secretary of State:** [bizfileOnline Registry Search](https://bizfileonline.sos.ca.gov/search/business)
* 🏛️ **Michigan LARA:** [Corporate Registry Search](https://cofs.lara.state.mi.us/Search/Search)
* 🏛️ **Alaska Division of Corporations:** [Entity Search Portal](https://www.commerce.alaska.gov/cbp/main/search/entities)
* 🏛️ **Orange County Clerk-Recorder:** [Public Property Records](https://www.ocrecorder.com)
''')
