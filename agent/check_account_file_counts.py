import json
from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

with open("agent/target_accounts_master.json") as f:
    d = json.load(f)

all_accounts = set(
    d["primary_gmail_accounts"] +
    d["new_gmail_accounts"] +
    d["microsoft_onedrive_accounts"] +
    d["google_workspace_edu"] +
    d["firefox_browser_profiles"]
)

print(f"=== CHECKING DRIVE & ONEDRIVE FILE COUNTS FOR {len(all_accounts)} ACCOUNTS ===")

for acc in sorted(all_accounts):
    sql_drive = f"SELECT count(*) as cnt FROM `noble-beanbag-497411-m4.national_audits.drive_file_index` WHERE LOWER(file_name) LIKE '%{acc.lower()}%' OR LOWER(web_view_link) LIKE '%{acc.lower()}%'"
    rows_drive = list(client.query(sql_drive).result())
    cnt_drive = rows_drive[0].cnt

    sql_one = f"SELECT count(*) as cnt FROM `noble-beanbag-497411-m4.onedrive_forensics.onedrive_documents` WHERE LOWER(file_name) LIKE '%{acc.lower()}%' OR LOWER(file_path) LIKE '%{acc.lower()}%'"
    rows_one = list(client.query(sql_one).result())
    cnt_one = rows_one[0].cnt

    if cnt_drive > 0 or cnt_one > 0:
        print(f"[+] {acc}: {cnt_drive} Drive files | {cnt_one} OneDrive files")
    else:
        print(f"[-] {acc}: 0 Drive files | 0 OneDrive files (Ready for live sync)")
