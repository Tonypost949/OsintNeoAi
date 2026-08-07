# analyze_rico_full_v1_gemini.py
# Comprehensive RICO pattern analysis using Gemini Interactions API.
# Prerequisites: Set GEMINI_API_KEY env var, google-genai and google-cloud-bigquery installed.

from google import genai
from google.cloud import bigquery
import pandas as pd
import time

# Initialise clients
client = genai.Client()
bq = bigquery.Client()

def fetch_sample(table_id: str, limit: int = 500):
    """Fetch a limited sample of rows from a BigQuery table for quick analysis."""
    query = f"""
        SELECT *
        FROM `{table_id}`
        LIMIT {limit}
    """
    return bq.query(query).to_dataframe()

def gemini_summarize(df: pd.DataFrame, description: str) -> str:
    """Ask Gemini to surface patterns in the provided dataframe (as CSV)."""
    # Limit rows to keep prompt size reasonable
    csv_data = df.head(30).to_csv(index=False)
    prompt = f"""
You are an expert OSINT analyst. Using the CSV data below, identify any patterns, relationships, or anomalies that could indicate coordinated RICO activity. Highlight:
- Repeated entities, addresses, or identifiers across rows.
- Temporal clusters (many events on the same date).
- Any obvious hub‑and‑spoke structures.
- Suspicious financial flows or ownership links.
Provide a concise summary (max 200 words) and suggest the next investigative query.

Data description: {description}
CSV data:
{csv_data}
"""
    for model_name in ["gemini-3.5-flash", "gemini-3.1-pro-preview"]:
        try:
            interaction = client.interactions.create(
                model=model_name,
                input=prompt,
                store=False,
            )
            return interaction.output_text or "<no response>"
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            time.sleep(2)
    return "<no response due to repeated failures>"

def main():
    tables = {
        "rico_matches": "project-743aab84-f9a5-4ec7-954.ppp_rico.rico_matches",
        "rico_evidence_matrix": "project-743aab84-f9a5-4ec7-954.ppp_rico.rico_evidence_matrix",
        "hb_llcs": "project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs",
        "ppp_150k_plus": "project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus",
        "ppp_up_to_150k": "project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k",
    }
    for name, table_id in tables.items():
        print(f"\n=== Analyzing {name} ({table_id}) ===")
        df = fetch_sample(table_id)
        summary = gemini_summarize(df, f"Table {name} containing relevant RICO data")
        print(summary)

if __name__ == "__main__":
    main()
