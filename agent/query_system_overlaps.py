from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

def safe_money(val):
    if val is None:
        return "N/A"
    return f"${float(val):,.2f}"

print("=== CHDO Real Estate Transactions ===")
q_chdo = "SELECT * FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.chdo_real_estate_transactions`"
try:
    results_chdo = list(client.query(q_chdo).result())
    print(f"Found {len(results_chdo)} records:")
    for r in results_chdo:
        amt = safe_money(r.amount)
        print(f"CHDO LLC: {r.chdo_llc} | Project: {r.project_name} | Type: {r.transaction_type} | Amount: {amt} | Counterparty: {r.lp_entity_counterparty}")
        print(f"Notes: {r.terms_notes} | Flags: {r.flags}")
        print("-" * 50)
except Exception as e:
    print(f"Error querying chdo_real_estate_transactions: {e}")

print("\n=== Mercy House Schedule I ===")
q_mercy = "SELECT * FROM `project-743aab84-f9a5-4ec7-954.national_audits.mercy_house_schedule_i`"
try:
    results_mercy = list(client.query(q_mercy).result())
    print(f"Found {len(results_mercy)} records:")
    for r in results_mercy:
        grants = safe_money(r.total_government_grants)
        misclass = safe_money(r.misclassified_grant_amount)
        print(f"Org: {r.organization_name} | Year: {r.fiscal_year} | Govt Grants: {grants} | Misclassified: {misclass}")
        print(f"Notes: {r.misclassification_notes}")
        print(f"Grants JSON: {r.grants_json[:300] if r.grants_json else 'None'}...")
        print("-" * 50)
except Exception as e:
    print(f"Error querying mercy_house_schedule_i: {e}")
