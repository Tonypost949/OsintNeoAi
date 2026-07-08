import csv
import os
from collections import defaultdict

WORK_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work"

ORANGE_COUNTY_CITIES = {
    "ANAHEIM", "BREA", "BUENA PARK", "COSTA MESA", "CYPRESS", "DANA POINT",
    "FOUNTAIN VALLEY", "FULLERTON", "GARDEN GROVE", "HUNTINGTON BEACH",
    "IRVINE", "LA HABRA", "LA PALMA", "LAGUNA BEACH", "LAGUNA HILLS",
    "LAGUNA NIGUEL", "LAGUNA WOODS", "LAKE FOREST", "LOS ALAMITOS",
    "MISSION VIEJO", "NEWPORT BEACH", "ORANGE", "PLACENTIA", "RANCHO SANTA MARGARITA",
    "SAN CLEMENTE", "SAN JUAN CAPISTRANO", "SANTA ANA", "SEAL BEACH",
    "STANTON", "TUSTIN", "VILLA PARK", "WESTMINSTER", "YORBA LINDA",
    "ALISO VIEJO", "COTO DE CAZA", "LADERA RANCH", "LAS FLORES", "MIDWAY CITY",
    "NORTH TUSTIN", "ROSSMOOR", "SILVERADO", "SUNSET BEACH", "TRABUCO CANYON",
    "HUNTINGTON HARBOUR"
}

def load_csv(path):
    full_path = os.path.join(WORK_DIR, path)
    if not os.path.exists(full_path):
        return []
    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
        return list(csv.DictReader(f))

def normalize(name):
    return str(name).upper().strip().replace(",", "").replace("  ", " ")

def is_ca_or_oc_city(city):
    c = str(city).upper().strip()
    return c == "CA" or c in ORANGE_COUNTY_CITIES or c.endswith(", CA")

def is_out_of_state(state, city):
    s = str(state).upper().strip()
    c = str(city).upper().strip()
    if s and s != "CA":
        return True
    if c and c not in ORANGE_COUNTY_CITIES and c != "CA":
        # Could be other CA city; only mark out-of-state if state is explicit
        return False
    return False

suspicious_network = load_csv("suspicious_hb_network.csv")
ppp_rico = load_csv("ppp_rico_matches.csv")
church_entities = load_csv("hb_church_osint_entities.csv")
rico_matrix = load_csv("rico_evidence_matrix.csv")

entities = defaultdict(lambda: {
    "sources": set(),
    "reasons": set(),
    "properties": defaultdict(list),
    "is_local": False,
    "has_property": False
})

# 1. Suspicious HB network (local OC properties + out-of-state PPP)
for row in suspicious_network:
    name = normalize(row.get("owner_name", ""))
    if not name:
        continue

    prop_city = str(row.get("property_mail_city", "")).upper().strip()
    prop_state = str(row.get("property_mail_state", "")).upper().strip()
    ppp_city = str(row.get("ppp_borrower_city", "")).upper().strip()
    ppp_state = str(row.get("ppp_borrower_state", "")).upper().strip()

    entities[name]["sources"].add("suspicious_hb_network")
    entities[name]["properties"]["property_address"].append(row.get("property_address", ""))
    entities[name]["properties"]["mail_city"].append(row.get("property_mail_city", ""))
    entities[name]["properties"]["mail_state"].append(row.get("property_mail_state", ""))
    entities[name]["properties"]["ppp_amount"].append(row.get("ppp_amount", ""))
    entities[name]["properties"]["ppp_borrower_city"].append(row.get("ppp_borrower_city", ""))
    entities[name]["properties"]["ppp_borrower_state"].append(row.get("ppp_borrower_state", ""))
    entities[name]["properties"]["ppp_loan_status"].append(row.get("ppp_loan_status", ""))

    if prop_state == "CA" or (not prop_state and prop_city in ORANGE_COUNTY_CITIES):
        entities[name]["is_local"] = True
    if row.get("property_address", ""):
        entities[name]["has_property"] = True

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

    mail_city = str(row.get("mail_city", "")).upper().strip()
    loan_locs = str(row.get("loan_locations", "")).upper()

    entities[name]["sources"].add("ppp_rico_matches")
    entities[name]["properties"]["property_address"].append(row.get("property_address", ""))
    entities[name]["properties"]["mail_city"].append(row.get("mail_city", ""))
    entities[name]["properties"]["ppp_total_amount"].append(row.get("ppp_total_amount", ""))
    entities[name]["properties"]["ppp_total_forgiven"].append(row.get("ppp_total_forgiven", ""))
    entities[name]["properties"]["loan_locations"].append(row.get("loan_locations", ""))
    entities[name]["properties"]["ppp_loan_count"].append(row.get("ppp_loan_count", ""))

    if mail_city in ORANGE_COUNTY_CITIES:
        entities[name]["is_local"] = True
    if "CA" in loan_locs or any(c in loan_locs for c in ORANGE_COUNTY_CITIES):
        entities[name]["is_local"] = True

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

# 3. Church entities — ONLY include if CA / OC local
for row in church_entities:
    name = normalize(row.get("name", ""))
    if not name:
        continue

    city = str(row.get("city", "")).upper().strip()
    state = str(row.get("state", "")).upper().strip()

    # Skip non-CA churches entirely for focused OC grant list
    if state and state != "CA":
        continue
    if city and city not in ORANGE_COUNTY_CITIES and state != "CA":
        continue
    if not state and city not in ORANGE_COUNTY_CITIES:
        continue

    entities[name]["sources"].add("hb_church_osint_entities")
    entities[name]["properties"]["address"].append(row.get("address", ""))
    entities[name]["properties"]["city"].append(row.get("city", ""))
    entities[name]["properties"]["state"].append(row.get("state", ""))
    entities[name]["properties"]["ein"].append(row.get("ein", ""))

    entities[name]["is_local"] = True
    entities[name]["reasons"].add("ppp_church_entity")

# 4. RICO evidence matrix
for row in rico_matrix:
    name = normalize(row.get("llc_name", row.get("entity_name", row.get("name", ""))))
    if not name:
        continue
    entities[name]["sources"].add("rico_evidence_matrix")
    entities[name]["properties"]["evidence"].append(str(row))
    entities[name]["reasons"].add("rico_evidence")

# Filter to focused list: local OR has severe flags
focused_entities = {}
for name, data in entities.items():
    reasons = data["reasons"]
    is_local = data["is_local"]
    has_property = data["has_property"]

    # Include if:
    # - local OC/CA entity with any flag
    # - has HB property
    # - has severe flags (RICO, suspicious network, multiple PPP loans)
    severe_flags = {"rico_evidence", "suspicious_network_match", "ppp_fraud_multiple_loans", "ppp_rico_match"}
    if is_local or has_property or bool(reasons & severe_flags):
        focused_entities[name] = data

# Build output
output_rows = []
for name, data in sorted(focused_entities.items()):
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

output_path = os.path.join(WORK_DIR, "grant_disqualified_entities_focused.csv")
fieldnames = ["entity_name", "disqualification_reasons", "data_sources", "property_address", "mail_city", "ppp_amounts", "loan_locations"]

with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_rows)

print(f"Focused (OC-relevant) entities disqualified: {len(focused_entities)}")
print(f"Saved to: {output_path}")
print("\nReason breakdown:")
reason_counts = defaultdict(int)
for data in focused_entities.values():
    for reason in data["reasons"]:
        reason_counts[reason] += 1
for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
    print(f"  {reason}: {count}")
