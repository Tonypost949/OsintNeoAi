"""
Synthetic OSINT Dataset Generator for Benchmarking Graph Correlation Engine.

Generates realistic mock Nevada SOS business entities, SBA PPP loan records,
municipal property records, IRS 990 non-profit filings, and baseline graph JSON
files (nodes.json, edges.json) featuring controlled high-degree address hubs.
"""
import argparse
import csv
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Union, Tuple


# Predefined realistic address hubs (Registered Agent virtual offices / commercial hubs)
MOCK_ADDRESS_HUBS = [
    {"street": "101 N CARSON ST STE 200", "city": "CARSON CITY", "state": "NV", "zip": "89701"},
    {"street": "701 S CARSON ST", "city": "CARSON CITY", "state": "NV", "zip": "89701"},
    {"street": "311 S DIVISION ST", "city": "CARSON CITY", "state": "NV", "zip": "89703"},
    {"street": "251 JEANNE DR", "city": "RENO", "state": "NV", "zip": "89512"},
    {"street": "502 E JOHN ST", "city": "CARSON CITY", "state": "NV", "zip": "89706"},
]

FIRST_NAMES = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

CORP_PREFIXES = ["Apex", "Beacon", "Crest", "Delta", "Eagle", "Frontier", "Global", "Horizon", "Ironclad", "Jupiter", "Keystone", "Liberty", "Matrix", "Nexus", "Omega", "Pinnacle", "Quantum", "Summit", "Titan", "Vanguard"]
CORP_TYPES = ["Holdings LLC", "Ventures Inc", "Capital LLC", "Properties Corp", "Services LLC", "Partners LP", "Consulting Group LLC", "Enterprises Inc"]
STREET_NAMES = ["Main St", "Carson St", "Virginia St", "Market St", "Commercial Row", "Lake Blvd", "Sierra St", "Center St"]
CITIES = ["Carson City", "Reno", "Las Vegas", "Henderson", "Sparks"]


def generate_person_name(rng: random.Random) -> str:
    """Generate realistic full person name."""
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def generate_business_name(rng: random.Random) -> str:
    """Generate realistic business entity name."""
    return f"{rng.choice(CORP_PREFIXES)} {rng.choice(CORP_TYPES)}"


def generate_random_address(rng: random.Random, hubs: List[Dict[str, str]], use_hub_prob: float = 0.35) -> Tuple[str, str, str, str]:
    """Generate an address tuple (street, city, state, zip), randomly choosing a shared hub."""
    if rng.random() < use_hub_prob and hubs:
        hub = rng.choice(hubs)
        return hub["street"], hub["city"], hub["state"], hub["zip"]
    
    number = rng.randint(100, 9999)
    street = f"{number} {rng.choice(STREET_NAMES)}"
    city = rng.choice(CITIES)
    state = "NV"
    zip_code = f"89{rng.randint(10, 99)}"
    return street, city, state, zip_code


def generate_synthetic_osint_dataset(
    output_dir: Union[str, Path],
    num_nodes: int = 1000,
    num_hubs: int = 5,
    seed: int = 42
) -> Dict[str, Path]:
    """
    Generate synthetic OSINT datasets with controlled address hubs and cross-dataset links.

    Args:
        output_dir: Path to directory where CSV and JSON files will be saved.
        num_nodes: Approximate target node volume to scale records.
        num_hubs: Number of high-degree address hubs to inject.
        seed: Random seed for deterministic reproducibility.

    Returns:
        Dict mapping file dataset key to output Path object.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    selected_hubs = MOCK_ADDRESS_HUBS[:min(num_hubs, len(MOCK_ADDRESS_HUBS))]

    # Scale count per file based on total requested nodes
    record_count = max(10, num_nodes // 4)

    # Maintain a pool of shared names for cross-linking
    shared_names = [generate_person_name(rng) for _ in range(max(5, record_count // 5))]

    # 1. Nevada SOS CSV
    nevada_sos_file = output_path / "nevada_sos.csv"
    nevada_rows = []
    for i in range(record_count):
        entity_id = f"NV2026{i+10000:06d}"
        biz_name = generate_business_name(rng)
        entity_type = rng.choice(["Limited Liability Company", "Corporation", "Limited Partnership"])
        status = rng.choice(["Active", "Active", "Active", "Default", "Dissolved"])
        filing_date = f"202{rng.randint(0,6)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}"
        
        ra_name = f"{generate_person_name(rng)} Registered Agent Services"
        ra_street, ra_city, ra_state, ra_zip = generate_random_address(rng, selected_hubs, use_hub_prob=0.5)
        ra_address = f"{ra_street}, {ra_city}, {ra_state} {ra_zip}"
        
        officer_name = rng.choice(shared_names) if rng.random() < 0.4 else generate_person_name(rng)
        off_street, off_city, off_state, off_zip = generate_random_address(rng, selected_hubs, use_hub_prob=0.3)
        off_address = f"{off_street}, {off_city}, {off_state} {off_zip}"

        nevada_rows.append({
            "Entity_ID": entity_id,
            "Business_Name": biz_name,
            "Entity_Type": entity_type,
            "Status": status,
            "Filing_Date": filing_date,
            "Registered_Agent_Name": ra_name,
            "Registered_Agent_Address": ra_address,
            "Officer_Name": officer_name,
            "Officer_Title": "Manager / President",
            "Officer_Address": off_address
        })

    with open(nevada_sos_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=nevada_rows[0].keys())
        writer.writeheader()
        writer.writerows(nevada_rows)

    # 2. SBA PPP Loans CSV
    sba_file = output_path / "sba_ppp_loans.csv"
    sba_rows = []
    for i in range(record_count):
        loan_num = f"PPP{i+500000:07d}"
        borrower_name = generate_business_name(rng) if rng.random() > 0.3 else nevada_rows[i % len(nevada_rows)]["Business_Name"]
        street, city, state, zip_code = generate_random_address(rng, selected_hubs, use_hub_prob=0.4)
        amount = round(rng.uniform(10000, 500000), 2)
        jobs = rng.randint(1, 50)
        date_approved = f"2020-{rng.randint(4,6):02d}-{rng.randint(1,28):02d}"

        sba_rows.append({
            "LoanNumber": loan_num,
            "BorrowerName": borrower_name,
            "BorrowerAddress": street,
            "City": city,
            "State": state,
            "Zip": zip_code,
            "CurrentApprovalAmount": amount,
            "JobsReported": jobs,
            "DateApproved": date_approved,
            "Lender": "Bank of Nevada",
            "BusinessTypeValue": "Limited Liability Company(LLC)"
        })

    with open(sba_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sba_rows[0].keys())
        writer.writeheader()
        writer.writerows(sba_rows)

    # 3. Property Records CSV
    prop_file = output_path / "property_records.csv"
    prop_rows = []
    for i in range(record_count):
        parcel_id = f"PAR-041-{i+1000:04d}"
        street, city, state, zip_code = generate_random_address(rng, selected_hubs, use_hub_prob=0.3)
        prop_addr = f"{street}, {city}, {state} {zip_code}"
        owner_name = rng.choice(shared_names) if rng.random() < 0.4 else nevada_rows[i % len(nevada_rows)]["Business_Name"]
        value = rng.randint(250000, 2500000)

        prop_rows.append({
            "Parcel_ID": parcel_id,
            "Property_Address": prop_addr,
            "Owner_Name": owner_name,
            "Assessed_Value": value,
            "Property_Type": "Commercial",
            "Sale_Date": f"201{rng.randint(5,9)}-0{rng.randint(1,9):01d}-15",
            "Sale_Price": value + rng.randint(10000, 50000)
        })

    with open(prop_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=prop_rows[0].keys())
        writer.writeheader()
        writer.writerows(prop_rows)

    # 4. IRS 990 CSV
    irs_file = output_path / "irs_990.csv"
    irs_rows = []
    for i in range(max(5, record_count // 2)):
        ein = f"88-{i+1000000:07d}"
        org_name = f"Nevada {rng.choice(CORP_PREFIXES)} Foundation"
        street, city, state, zip_code = generate_random_address(rng, selected_hubs, use_hub_prob=0.4)
        officer = rng.choice(shared_names)

        irs_rows.append({
            "EIN": ein,
            "Organization_Name": org_name,
            "Address": street,
            "City": city,
            "State": state,
            "Zip": zip_code,
            "Tax_Year": 2024,
            "Total_Revenue": rng.randint(50000, 10000000),
            "Principal_Officer": officer
        })

    with open(irs_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=irs_rows[0].keys())
        writer.writeheader()
        writer.writerows(irs_rows)

    # 5. Baseline Graph JSON (nodes.json and edges.json)
    nodes_file = output_path / "nodes.json"
    edges_file = output_path / "edges.json"

    nodes_list = []
    edges_list = []

    # Create NodeDTOs and EdgeDTOs matching Pydantic contract
    for idx, row in enumerate(nevada_rows):
        biz_node_id = f"biz_{row['Entity_ID']}"
        officer_node_id = f"person_{idx}"
        addr_node_id = f"addr_hub_{idx % max(1, num_hubs)}"

        nodes_list.append({
            "node_id": biz_node_id,
            "node_type": "BUSINESS",
            "label": row["Business_Name"],
            "normalized_label": row["Business_Name"].upper(),
            "address_id": addr_node_id,
            "metadata": {"source": "nevada_sos", "status": row["Status"]}
        })

        nodes_list.append({
            "node_id": officer_node_id,
            "node_type": "PERSON",
            "label": row["Officer_Name"],
            "normalized_label": row["Officer_Name"].upper(),
            "address_id": None,
            "metadata": {"title": row["Officer_Title"]}
        })

        edges_list.append({
            "edge_id": f"edge_owns_{idx}",
            "source_id": officer_node_id,
            "target_id": biz_node_id,
            "edge_type": "OWNS",
            "confidence": 1.0,
            "metadata": {"relationship": "Officer/Owner"}
        })

        edges_list.append({
            "edge_id": f"edge_reg_{idx}",
            "source_id": biz_node_id,
            "target_id": addr_node_id,
            "edge_type": "REGISTERED_AT",
            "confidence": 1.0,
            "metadata": {}
        })

    with open(nodes_file, "w", encoding="utf-8") as f:
        json.dump(nodes_list, f, indent=2)

    with open(edges_file, "w", encoding="utf-8") as f:
        json.dump(edges_list, f, indent=2)

    return {
        "nevada_sos": nevada_sos_file,
        "sba_ppp_loans": sba_file,
        "property_records": prop_file,
        "irs_990": irs_file,
        "nodes": nodes_file,
        "edges": edges_file,
    }


def main():
    """CLI Entry Point for mock OSINT dataset generation."""
    parser = argparse.ArgumentParser(description="Generate synthetic OSINT benchmark dataset.")
    parser.add_argument("--output-dir", type=str, default="data/mock", help="Directory path to save dataset files.")
    parser.add_argument("--num-nodes", type=int, default=1000, help="Target total node volume.")
    parser.add_argument("--num-hubs", type=int, default=5, help="Number of shared address hubs.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")

    args = parser.parse_args()
    results = generate_synthetic_osint_dataset(
        output_dir=args.output_dir,
        num_nodes=args.num_nodes,
        num_hubs=args.num_hubs,
        seed=args.seed
    )
    print(f"Successfully generated synthetic OSINT dataset in '{args.output_dir}':")
    for key, path in results.items():
        print(f"  - {key}: {path}")


if __name__ == "__main__":
    main()
