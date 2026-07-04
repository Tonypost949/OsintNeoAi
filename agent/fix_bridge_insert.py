import pandas as pd
from google.cloud import bigquery
import ast
import os

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
TABLE = "project-743aab84-f9a5-4ec7-954.ppp_rico.hb_ppp_bridge"

# ── Find the CSV ──────────────────────────────────────────────────────────────
CSV_CANDIDATES = [
    r"C:\Users\HP\Downloads\hb_ppp_bridge.csv",
    r"C:\Users\HP\Downloads\bridge_results.csv",
    r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\hb_ppp_bridge.csv",
    r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\bridge_results.csv",
]
csv_path = None
for p in CSV_CANDIDATES:
    if os.path.exists(p):
        csv_path = p
        break

if not csv_path:
    # Try to find it anywhere in Downloads
    import glob
    hits = glob.glob(r"C:\Users\HP\Downloads\*.csv")
    print("No bridge CSV found. CSVs in Downloads:")
    for h in hits:
        print(" ", h)
    raise FileNotFoundError("Place the bridge CSV in Downloads and re-run.")

print(f"Found CSV: {csv_path}")
df = pd.read_csv(csv_path)
print(f"Rows: {len(df)}  |  Columns: {list(df.columns)}")

# ── Column Mapping ────────────────────────────────────────────────────────────
def safe_first(val):
    """Pull first element if val looks like a list/array string."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s.startswith("["):
        try:
            items = ast.literal_eval(s)
            return str(items[0]) if items else None
        except Exception:
            pass
    return s if s not in ("", "nan", "None") else None

def to_bool_flag(val, true_condition_fn):
    try:
        return bool(true_condition_fn(val))
    except Exception:
        return False

rows = []
for _, r in df.iterrows():
    # Derive boolean flags
    ppp_states_raw = str(r.get("ppp_states", "")).strip()
    multi_state = False
    if ppp_states_raw and ppp_states_raw not in ("nan", "None", ""):
        try:
            states_list = ast.literal_eval(ppp_states_raw) if ppp_states_raw.startswith("[") else [ppp_states_raw]
            multi_state = len(set(states_list)) > 1
        except Exception:
            multi_state = False

    hb_mail = str(r.get("hb_mail", "")).strip()
    hb_address = str(r.get("hb_address", "")).strip()
    is_mailbox = (hb_mail != hb_address and hb_mail not in ("", "nan", "None"))

    sale_value = r.get("hb_sale_value", None)
    try:
        is_zero = float(sale_value) == 0.0
    except (TypeError, ValueError):
        is_zero = False

    # Derive post-PPP acquisition (PPP loans 2020-2021, check if sale date is after)
    sale_date = str(r.get("hb_sale_date", "")).strip()
    is_post_ppp = False
    if sale_date not in ("", "nan", "None"):
        try:
            from datetime import datetime
            dt = datetime.strptime(sale_date[:10], "%Y-%m-%d")
            is_post_ppp = dt.year >= 2021
        except Exception:
            pass

    # NAICS mismatch — flag if ppp_naics contains non-housing codes while entity is housing
    naics_raw = str(r.get("ppp_naics", "")).strip()
    is_naics_mismatch = False
    if naics_raw not in ("", "nan", "None"):
        try:
            naics_list = ast.literal_eval(naics_raw) if naics_raw.startswith("[") else [naics_raw]
            # Housing NAICS codes start with 623 (residential care) or 624 (social services)
            is_naics_mismatch = any(not str(n).startswith(("623", "624", "531")) for n in naics_list)
        except Exception:
            pass

    row = {
        "entity_name":                    str(r.get("entity", "")).strip() or None,
        "property_address":               str(r.get("hb_address", "")).strip() or None,
        "property_city":                  "Huntington Beach",  # All HB targets
        "property_apn":                   str(r.get("hb_apn", "")).strip() or None,
        "property_mail_address":          str(r.get("hb_mail", "")).strip() or None,
        "property_mail_city":             str(r.get("hb_mail_city", "")).strip() or None,
        "last_seller":                    str(r.get("hb_seller", "")).strip() or None,
        "property_acquisition_date":      sale_date or None,
        "property_acquisition_value":     float(sale_value) if sale_value and str(sale_value) not in ("nan","None","") else None,
        "ppp_loan_count":                 int(r["ppp_loan_count"]) if pd.notna(r.get("ppp_loan_count")) else None,
        "ppp_total_amount":               float(r["ppp_total_amount"]) if pd.notna(r.get("ppp_total_amount")) else None,
        "ppp_total_forgiven":             float(r["ppp_total_forgiven"]) if pd.notna(r.get("ppp_total_forgiven")) else None,
        "ppp_business_addresses":         None,  # Not in CSV — leave null
        "ppp_state_array":                ppp_states_raw if ppp_states_raw not in ("nan","None","") else None,
        "ppp_naics_codes":                naics_raw if naics_raw not in ("nan","None","") else None,
        "ppp_lenders":                    str(r.get("ppp_lenders", "")).strip() or None,
        "ppp_borrower_address":           None,  # Not in CSV
        "ppp_borrower_city":              safe_first(r.get("ppp_cities")),
        "ppp_borrower_state":             safe_first(r.get("ppp_states")),
        "is_multi_state_ppp":             multi_state,
        "is_naics_mismatch":              is_naics_mismatch,
        "is_post_ppp_property_acquisition": is_post_ppp,
        "is_mailbox_address":             is_mailbox,
        "is_zero_dollar_transfer":        is_zero,
    }
    rows.append(row)

mapped_df = pd.DataFrame(rows)
print(f"\nMapped {len(mapped_df)} rows. Sample:")
print(mapped_df.head(3).to_string())

# ── Insert to BigQuery ────────────────────────────────────────────────────────
job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    autodetect=False,
)

job = bq.load_table_from_dataframe(mapped_df, TABLE, job_config=job_config)
job.result()
print(f"\n✅ Successfully inserted {len(mapped_df)} rows into {TABLE}")

# ── Quick investigation summary ───────────────────────────────────────────────
print("\n── Top Entities by PPP Amount ──")
q = f"""
SELECT entity_name, ppp_loan_count, ppp_total_amount, ppp_total_forgiven,
       is_multi_state_ppp, is_naics_mismatch, is_post_ppp_property_acquisition,
       is_zero_dollar_transfer
FROM `{TABLE}`
ORDER BY ppp_total_amount DESC
LIMIT 20
"""
result = bq.query(q).to_dataframe()
print(result.to_string())
