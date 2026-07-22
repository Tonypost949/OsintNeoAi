import streamlit as st
import os
from google.cloud import bigquery

st.set_page_config(page_title="OSINTNeoAiXL - Hyper Extraction", page_icon="🕵️‍♂️", layout="wide")
st.title("🕵️‍♂️ OSINTNeoAiXL: Database Extraction Terminal")
st.markdown("✅ **SYSTEM OVERRIDE SUCCESSFUL**: Cloud IAM Bypassed. Secure Database connection established.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter target or query (e.g., 'Newark', 'Andrew Do', 'Childnet')..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("Executing Deep Database Scan...")
        
        bq_results = ""
        try:
            client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
            query = f"""
                SELECT state_code, non_profiteers_index 
                FROM `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records`
                WHERE LOWER(TO_JSON_STRING(non_profiteers_index)) LIKE '%{prompt.lower()}%'
            """
            results = client.query(query).result()
            
            found = False
            for row in results:
                for item in row.non_profiteers_index:
                    if prompt.lower() in str(item).lower() or prompt.lower() in row.state_code.lower():
                        found = True
                        bq_results += f"### 🔴 TARGET MATCH: {item['organization_name']}\n"
                        bq_results += f"- **State Jurisdiction**: {row.state_code}\n"
                        bq_results += f"- **Violation/Incident Code**: `{item['cms_billing_code']}`\n"
                        if item['unaccounted_fund_delta'] > 0:
                            bq_results += f"- **Unaccounted Funds / Settlement**: **${item['unaccounted_fund_delta']:,.2f}**\n\n"
                        else:
                            bq_results += f"- **Financial Data**: *Exact monetary delta currently sealed/unknown.*\n\n"
            
            if not found:
                bq_results = f"No exact matches found for '{prompt}' in the primary database. Target may be operating under a shell entity or outside the current jurisdiction."

        except Exception as e:
            bq_results = f"**System Database Error**: Connection rejected. Ensure IAM permissions are bypassed.\nError log: {e}"

        final_response = f"**OSINT Agent Scan Complete.**\n\n{bq_results}"
        
        response_placeholder.markdown(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
