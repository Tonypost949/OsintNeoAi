import streamlit as st
import os
import json
from google.cloud import bigquery

# Check if requested as a programmatic API endpoint (e.g. ?api=search&q=Huntington)
query_params = st.query_params
if "api" in query_params and query_params["api"] == "search":
    q = query_params.get("q", "").lower()
    gcp_project_id = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
    client = bigquery.Client(project=gcp_project_id)
    query = f"""
        SELECT state_code, non_profiteers_index 
        FROM `{gcp_project_id}.national_audits.all_state_records`
        WHERE LOWER(TO_JSON_STRING(non_profiteers_index)) LIKE @search_term
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("search_term", "STRING", f"%{q}%")
        ]
    )
    results = client.query(query, job_config=job_config).result()
    output_records = []
    for row in results:
        for item in row.non_profiteers_index:
            if q in str(item).lower() or q in row.state_code.lower():
                output_records.append({
                    "state_code": row.state_code,
                    "organization_name": item["organization_name"],
                    "cms_billing_code": item["cms_billing_code"],
                    "unaccounted_fund_delta": item["unaccounted_fund_delta"]
                })
    st.write(json.dumps(output_records))
    st.stop()

st.set_page_config(page_title="OSINTNeoAiXL - Hyper Extraction", page_icon="🕵️‍♂️", layout="wide")
st.title("🕵️‍♂️ OSINTNeoAiXL: Database Extraction Terminal")

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
            gcp_project_id = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
            client = bigquery.Client(project=gcp_project_id)
            query = f"""
                SELECT state_code, non_profiteers_index 
                FROM `{gcp_project_id}.national_audits.all_state_records`
                WHERE LOWER(TO_JSON_STRING(non_profiteers_index)) LIKE @search_term
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("search_term", "STRING", f"%{prompt.lower()}%")
                ]
            )
            results = client.query(query, job_config=job_config).result()
            
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
