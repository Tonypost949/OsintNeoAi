import csv
import os
from collections import defaultdict

WORK_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work"

def load_csv(path):
    full_path = os.path.join(WORK_DIR, path)
    if not os.path.exists(full_path):
        return []
    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
        return list(csv.DictReader(f))

def normalize(name):
    return str(name).upper().strip().replace(",", "").replace("  ", " ")

suspicious_network = load_csv("suspicious_hb_network.csv")
ppp_rico = load_csv("ppp_rico_matches.csv")
rico_matrix = load_csv("rico_evidence_matrix.csv")

entities = defaultdict(lambda: {
    "sources": set(),
    "reasons": set(),
    "properties": defaultdict(list)
})

# 1. Suspicious HB network
for row in suspicious_network:
    name = normalize(row.get("owner_name", ""))
    if not name:
        continue

    prop_state = str(row.get("property_mail_state", "")).upper().strip()
    ppp_state = str(row.get("ppp_borrower_state", "")).upper().strip()

    entities[name]["sources"].add("suspicious_hb_network")
    entities[name]["properties"]["property_address"].append(row.get("property_address", ""))
    entities[name]["properties"]["mail_city"].append(row.get("property_mail_city", ""))
    entities[name]["properties"]["mail_state"].append(row.get("property_mail_state", ""))
    entities[name]["properties"]["ppp_amount"].append(row.get("ppp_amount", ""))
    entities[name]["properties"]["ppp_borrower_city"].append(row.get("ppp_borrower_city", ""))
    entities[name]["properties"]["ppp_borrower_state"].append(row.get("ppp_borrower_state", ""))
    entities[name]["properties"]["ppp_loan_status"].append(row.get("ppp_loan_status", ""))

    if prop_state and prop_state != "CA":
        entities[name]["reasons"].add("out_of_state_mail")

    if ppp_state and ppp_state != "CA":
        entities[name]["reasons"].add("ppp_out_of_state")

    if "LLC" in name or "INC" in name or "CORP" in name or "LP" in name:
        entities[name]["reasons"].add("llc_or_corp")

    try:
        amt = float(row.get("ppp_amount", "0") or 0)
        if amt > 150000:
            entities[name]["reasons"].add("high_ppp_amount")
    except ValueError:
        pass

    entities[name]["reasons"].add("suspicious_network_match")

# 2. PPP RICO matches
for row in ppp_rico:
    name = normalize(row.get("llc_name", ""))
    if not name:
        continue

    entities[name]["sources"].add("ppp_rico_matches")
    entities[name]["properties"]["property_address"].append(row.get("property_address", ""))
    entities[name]["properties"]["mail_city"].append(row.get("mail_city", ""))
    entities[name]["properties"]["ppp_total_amount"].append(row.get("ppp_total_amount", ""))
    entities[name]["properties"]["ppp_total_forgiven"].append(row.get("ppp_total_forgiven", ""))
    entities[name]["properties"]["loan_locations"].append(row.get("loan_locations", ""))
    entities[name]["properties"]["ppp_loan_count"].append(row.get("ppp_loan_count", ""))

    if "LLC" in name or "INC" in name or "CORP" in name or "LP" in name:
        entities[name]["reasons"].add("llc_or_corp")

    try:
        loan_count = int(row.get("ppp_loan_count", "0") or 0)
        if loan_count > 1:
            entities[name]["reasons"].add("ppp_fraud_multiple_loans")
    except ValueError:
        pass

    try:
        total = float(row.get("ppp_total_amount", "0") or 0)
        if total > 150000:
            entities[name]["reasons"].add("high_ppp_amount")
    except ValueError:
        pass

    entities[name]["reasons"].add("ppp_rico_match")

# 3. RICO evidence matrix
for row in rico_matrix:
    name = normalize(row.get("llc_name", row.get("entity_name", row.get("name", ""))))
    if not name:
        continue
    entities[name]["sources"].add("rico_evidence_matrix")
    entities[name]["properties"]["evidence"].append(str(row))
    entities[name]["reasons"].add("rico_evidence")

# Fraud-only: exclude entities flagged ONLY for being a church
fraud_only = {}
for name, data in entities.items():
    reasons = data["reasons"]
    # Exclude if only reason is generic church/religious
    if not reasons:
        continue
    fraud_only[name] = data

# Build output
output_rows = []
for name, data in sorted(fraud_only.items()):
    reasons = "; ".join(sorted(data["reasons"]))
    sources = "; ".join(sorted(data["sources"]))
    props = data["properties"]

    property_address = " | ".join(filter(None, set(props.get("property_address", []))))[:200]
    mail_city = " | ".join(filter(None, set(props.get("mail_city", []))))[:100]
    ppp_amount = " | ".join(filter(None, set(props.get("ppp_amount", []) + props.get("ppp_total_amount", []))))[:100]
    loan_locations = " | ".join(filter(None, set(props.get("loan_locations", []))))[:200]

    output_rows.append({
        "entity_name": name,
        "disqualification_reasons": reasons,
        "data_sources": sources,
        "property_address": property_address,
        "mail_city": mail_city,
        "ppp_amounts": ppp_amount,
        "loan_locations": loan_locations,
    })

output_path = os.path.join(WORK_DIR, "grant_disqualified_entities_fraud_only.csv")
fieldnames = ["entity_name", "disqualification_reasons", "data_sources", "property_address", "mail_city", "ppp_amounts", "loan_locations"]

with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_rows)

print(f"Fraud-only entities disqualified: {len(fraud_only)}")
print(f"Saved to: {output_path}")
print("\nReason breakdown:")
reason_counts = defaultdict(int)
for data in fraud_only.values():
    for reason in data["reasons"]:
        reason_counts[reason] += 1
for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
    print(f"  {reason}: {count}")
