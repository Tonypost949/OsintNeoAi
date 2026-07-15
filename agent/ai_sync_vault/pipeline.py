"""
Integrated pipeline: download all 12 PPP sub-$150k parts, load to BQ, match, export.
"""
import os, sys, glob, requests, subprocess
from google.cloud import bigquery
from google.cloud.bigquery import SchemaField
import pandas as pd

# --- CONFIG ---
DIR = r"G:\ppp_rico_data"
PROJECT = "157249702170"
DATASET = "ppp_rico"
TABLE_SUB = "ppp_up_to_150k"
TABLE_150 = "ppp_150k_plus"
TABLE_LLC = "hb_llcs"
RESULTS_TABLE = "rico_evidence_matrix"
LLC_CSV = os.path.join(DIR, "HB_OutOfState_LLCs.csv")
F150_CSV = os.path.join(DIR, "public_150k_plus_240930.csv")
N_PARTS = 12

# All 12 sub-$150k resource IDs (verified via CKAN API, 2024-09-30 release)
RESOURCE_IDS = [
    "cff06664-1f75-4969-ab3d-6fa7d6b4c41e",  # 1
    "1e6b6629-a5aa-46e6-a442-6e67366d2362",  # 2
    "644c304a-f5ad-4cfa-b128-fe2cbcb7b26e",  # 3
    "98af633d-eb1b-4d4b-995d-330962e6c38d",  # 4
    "3b407e04-f269-47a0-a5fe-661d1a08a76c",  # 5
    "7b7b5b58-9645-4b88-a675-a8a825e77076",  # 6
    "dabdddb5-1807-44f6-97c6-d624a5372525",  # 7
    "1fc6ddc4-ccb0-49d4-b632-0749e3292e57",  # 8
    "e9f2c718-b95e-47da-8f3e-17154aab1c86",  # 9
    "d9972f0d-c377-46ac-8637-a5c1265377c8",  # 10
    "8db19ddc-f036-40df-89f9-d0d309aa58b5",  # 11
    "7e4f672f-d163-4735-a5ec-f23afa2835db",  # 12
]

BASE_URL = "https://data.sba.gov/dataset/8aa276e2-6cab-4f86-aca4-a7dde42adf24/resource"
OLD_NAMES = {"ppp_150k_plus.csv": "public_150k_plus_240930.csv", "ppp_up_to_150k.csv": "public_up_to_150k_1_240930.csv"}

PPP_SCHEMA = [
    SchemaField("LoanNumber", "STRING"), SchemaField("DateApproved", "STRING"),
    SchemaField("SBAOfficeCode", "STRING"), SchemaField("ProcessingMethod", "STRING"),
    SchemaField("BorrowerName", "STRING"), SchemaField("BorrowerAddress", "STRING"),
    SchemaField("BorrowerCity", "STRING"), SchemaField("BorrowerState", "STRING"),
    SchemaField("BorrowerZip", "STRING"), SchemaField("LoanStatusDate", "STRING"),
    SchemaField("LoanStatus", "STRING"), SchemaField("Term", "STRING"),
    SchemaField("SBAGuarantyPercentage", "STRING"),
    SchemaField("InitialApprovalAmount", "FLOAT"), SchemaField("CurrentApprovalAmount", "FLOAT"),
    SchemaField("UndisbursedAmount", "FLOAT"), SchemaField("FranchiseName", "STRING"),
    SchemaField("ServicingLenderLocationID", "STRING"), SchemaField("ServicingLenderName", "STRING"),
    SchemaField("ServicingLenderAddress", "STRING"), SchemaField("ServicingLenderCity", "STRING"),
    SchemaField("ServicingLenderState", "STRING"), SchemaField("ServicingLenderZip", "STRING"),
    SchemaField("RuralUrbanIndicator", "STRING"), SchemaField("HubzoneIndicator", "STRING"),
    SchemaField("LMIIndicator", "STRING"), SchemaField("BusinessAgeDescription", "STRING"),
    SchemaField("ProjectCity", "STRING"), SchemaField("ProjectCountyName", "STRING"),
    SchemaField("ProjectState", "STRING"), SchemaField("ProjectZip", "STRING"),
    SchemaField("CD", "STRING"), SchemaField("JobsReported", "FLOAT"),
    SchemaField("NAICSCode", "STRING"), SchemaField("Race", "STRING"),
    SchemaField("Ethnicity", "STRING"), SchemaField("UTILITIES_PROCEED", "FLOAT"),
    SchemaField("PAYROLL_PROCEED", "FLOAT"), SchemaField("MORTGAGE_INTEREST_PROCEED", "FLOAT"),
    SchemaField("RENT_PROCEED", "FLOAT"), SchemaField("REFINANCE_EIDL_PROCEED", "FLOAT"),
    SchemaField("HEALTH_CARE_PROCEED", "FLOAT"), SchemaField("DEBT_INTEREST_PROCEED", "FLOAT"),
    SchemaField("BusinessType", "STRING"), SchemaField("OriginatingLenderLocationID", "STRING"),
    SchemaField("OriginatingLender", "STRING"), SchemaField("OriginatingLenderCity", "STRING"),
    SchemaField("OriginatingLenderState", "STRING"), SchemaField("Gender", "STRING"),
    SchemaField("Veteran", "STRING"), SchemaField("NonProfit", "STRING"),
    SchemaField("ForgivenessAmount", "FLOAT"), SchemaField("ForgivenessDate", "STRING"),
]

# --- STEP 0: Rename existing files to canonical names ---
def step_rename():
    for old, new in OLD_NAMES.items():
        oldp = os.path.join(DIR, old)
        newp = os.path.join(DIR, new)
        if os.path.exists(oldp):
            if os.path.exists(newp):
                os.remove(oldp)
                print(f"  Removed {old} (already have {new})")
            else:
                os.rename(oldp, newp)
                print(f"  Renamed {old} -> {new}")

# --- STEP 1: Download missing parts ---
def step_download():
    for i in range(N_PARTS):
        rid = RESOURCE_IDS[i]
        fname = f"public_up_to_150k_{i+1}_240930.csv"
        path = os.path.join(DIR, fname)
        if os.path.exists(path):
            print(f"  [SKIP] {fname} ({os.path.getsize(path)/1e6:.0f} MB)")
            continue
        url = f"{BASE_URL}/{rid}/download/{fname}"
        print(f"  [DL] {fname} ...", end=" ", flush=True)
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        with open(path, "wb") as f:
            downloaded = 0
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
        mb = os.path.getsize(path) / 1e6
        print(f"{mb:.0f} MB")

# --- STEP 2: Load >$150k file ---
def step_load_150(client):
    f150 = os.path.join(DIR, "public_150k_plus_240930.csv")
    if not os.path.exists(f150):
        print("  [!] >$150k file not found, skipping")
        return
    table_ref = f"{PROJECT}.{DATASET}.{TABLE_150}"
    job_config = bigquery.LoadJobConfig(
        schema=PPP_SCHEMA, source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1, encoding="ISO-8859-1",
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        allow_quoted_newlines=True, max_bad_records=5000,
    )
    with open(f150, "rb") as f:
        client.load_table_from_file(f, table_ref, job_config=job_config).result()
    rows = client.get_table(table_ref).num_rows
    print(f"  [+] {TABLE_150}: {rows:,} rows")

# --- STEP 3: Load ALL sub-$150k parts into one table ---
def step_load_sub(client):
    table_ref = f"{PROJECT}.{DATASET}.{TABLE_SUB}"
    # First load part 1 with WRITE_TRUNCATE (creates table)
    part1 = os.path.join(DIR, "public_up_to_150k_1_240930.csv")
    if not os.path.exists(part1):
        print("  [!] Part 1 not found, aborting")
        return
    job_config = bigquery.LoadJobConfig(
        schema=PPP_SCHEMA, source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1, encoding="ISO-8859-1",
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        allow_quoted_newlines=True, max_bad_records=5000,
    )
    print("  Loading part 1...")
    with open(part1, "rb") as f:
        client.load_table_from_file(f, table_ref, job_config=job_config).result()
    total = client.get_table(table_ref).num_rows

    # Append parts 2-12
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
    for i in range(2, N_PARTS + 1):
        fname = f"public_up_to_150k_{i}_240930.csv"
        path = os.path.join(DIR, fname)
        if not os.path.exists(path):
            print(f"  [!] {fname} not found, skipping")
            continue
        print(f"  Appending part {i}...")
        with open(path, "rb") as f:
            client.load_table_from_file(f, table_ref, job_config=job_config).result()
    rows = client.get_table(table_ref).num_rows
    print(f"  [+] {TABLE_SUB}: {rows:,} rows total")

# --- STEP 4: Load LLCs ---
def step_load_llcs(client):
    df = pd.read_csv(LLC_CSV, encoding="latin1")
    df.columns = df.columns.str.strip()
    table_ref = f"{PROJECT}.{DATASET}.{TABLE_LLC}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, autodetect=True,
    )
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    rows = client.get_table(table_ref).num_rows
    print(f"  [+] {TABLE_LLC}: {rows:,} rows")

# --- STEP 5: Run matching query ---
def step_match(client):
    query = f"""
    CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.{RESULTS_TABLE}` AS
    WITH
    llc_clean AS (
        SELECT
            Owner1 AS llc_name, Owner2, SiteAddress AS property_address,
            MailAddress AS mail_address, MailCity AS mail_city, APN,
            LastSeller AS last_seller, LastSaleDate AS last_sale_date,
            SAFE_CAST(LastSaleValue AS FLOAT64) AS last_sale_value,
            UPPER(REGEXP_REPLACE(Owner1, r'[-.,&/()]', ' ')) AS clean_name
        FROM `{PROJECT}.{DATASET}.{TABLE_LLC}`
    ),
    ppp_all AS (
        SELECT BorrowerName, CurrentApprovalAmount AS loan_amount, DateApproved,
               BorrowerCity, BorrowerState, BorrowerZip, ForgivenessAmount, LoanStatus, BusinessType,
               UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/()]', ' ')) AS clean_name
        FROM `{PROJECT}.{DATASET}.{TABLE_150}`
        WHERE BorrowerName IS NOT NULL AND BorrowerName != 'Exemption 6'
        UNION ALL
        SELECT BorrowerName, CurrentApprovalAmount, DateApproved,
               BorrowerCity, BorrowerState, BorrowerZip, ForgivenessAmount, LoanStatus, BusinessType,
               UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/()]', ' ')) AS clean_name
        FROM `{PROJECT}.{DATASET}.{TABLE_SUB}`
        WHERE BorrowerName IS NOT NULL AND BorrowerName != 'Exemption 6'
    ),
    matches AS (
        SELECT l.llc_name, l.property_address, l.mail_city, l.last_sale_value,
               p.BorrowerName AS ppp_business_name, p.loan_amount, p.DateApproved,
               p.BorrowerCity AS ppp_city, p.BorrowerState AS ppp_state,
               p.BorrowerZip AS ppp_zip, p.ForgivenessAmount, p.LoanStatus
        FROM llc_clean l JOIN ppp_all p ON l.clean_name = p.clean_name
    )
    SELECT llc_name, property_address, mail_city, last_sale_value,
           COUNT(*) AS ppp_loan_count,
           ROUND(SUM(loan_amount), 2) AS ppp_total_amount,
           ROUND(SUM(ForgivenessAmount), 2) AS ppp_total_forgiven,
           STRING_AGG(DISTINCT ppp_business_name, '; ') AS ppp_names_matched,
           STRING_AGG(DISTINCT CONCAT('$', CAST(ROUND(loan_amount, 0) AS STRING), ' on ', DateApproved), '; ') AS loan_details,
           STRING_AGG(DISTINCT CONCAT(ppp_city, ', ', ppp_state), '; ') AS loan_locations,
           STRING_AGG(DISTINCT LoanStatus, '; ') AS loan_statuses
    FROM matches
    GROUP BY llc_name, property_address, mail_city, last_sale_value
    ORDER BY ppp_total_amount DESC;
    """
    print("  Running matching query...")
    client.query(query).result()
    rows = client.get_table(f"{PROJECT}.{DATASET}.{RESULTS_TABLE}").num_rows
    print(f"  [+] {RESULTS_TABLE}: {rows:,} rows")

# --- STEP 6: Export ---
def step_export(client):
    dest = os.path.join(DIR, "bq_rico_matches.csv")
    sql = f"SELECT * FROM `{PROJECT}.{DATASET}.{RESULTS_TABLE}` ORDER BY ppp_total_amount DESC"
    df = client.query(sql).to_dataframe()
    df.to_csv(dest, index=False)
    print(f"  [+] Exported to bq_rico_matches.csv ({len(df)} rows)")
    print()
    for _, r in df.iterrows():
        print(f"  {r['llc_name'][:35]:35s}  ${r['ppp_total_amount']:>9,.0f}  ${
            (r['ppp_total_forgiven'] or 0):>9,.0f}  {r['ppp_loan_count']:2d} loans  {r['loan_locations'][:45] if r['loan_locations'] else ''}")

# --- MAIN ---
def main():
    os.makedirs(DIR, exist_ok=True)
    os.chdir(DIR)
    print("=== PPP BigQuery Pipeline ===\n")

    print("[1/6] Rename existing files...")
    step_rename()

    print("\n[2/6] Download missing parts...")
    step_download()

    print("\n[3/6] Load to BigQuery...")
    client = bigquery.Client(project=PROJECT)
    step_load_150(client)
    step_load_sub(client)
    step_load_llcs(client)

    print("\n[4/6] Match...")
    step_match(client)

    print("\n[5/6] Export...")
    step_export(client)

    print("\n[6/6] Cleanup temp scripts...")
    for f in glob.glob(os.path.join(DIR, "bq_*.py")):
        if f != __file__:
            os.remove(f)

    print("\n=== DONE ===")

if __name__ == "__main__":
    main()
