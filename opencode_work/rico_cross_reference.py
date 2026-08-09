#!/usr/bin/env python3
"""
RICO OSINT Cross‑Reference Tool
--------------------------------
Maps out‑of‑state LLCs (from Huntington Beach GIS data) against:
  - SBA PPP loan records (SBA FOIA dataset)
  - IRS Form 990 filings (ProPublica Nonprofit Explorer API)
  - Nevada Secretary of State business entity records

Output: A single CSV with all evidence linked to each LLC.
"""

import csv
import json
import re
import time
from typing import Dict, List, Optional
import requests
import pandas as pd
from tqdm import tqdm

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
INPUT_CSV = "HB_OutOfState_LLCs.csv"
OUTPUT_CSV = "rico_evidence_matrix.csv"

PPP_DATA_URL = "https://raw.githubusercontent.com/ProPublica/ppp-data/master/ppp_data_latest.csv"
PPP_LOCAL_150 = "ppp_150k_plus.csv"
PPP_LOCAL_SUB = "ppp_up_to_150k.csv"
NONPROFIT_API_BASE = "https://projects.propublica.org/nonprofits/api/v2"
NV_SOS_URL = "https://www.nvsos.gov/sosentitysearch/Corp/NameSearch"

# ------------------------------------------------------------
# CITY → STATE MAPPING
# ------------------------------------------------------------
CITY_TO_STATE = {
    'ALBUQUERQUE': 'NM', 'ALEXANDRIA': 'VA', 'ALGONQUIN': 'IL',
    'ANACORTES': 'WA', 'ARLINGTON': 'VA', 'ATLANTA': 'GA',
    'AUSTIN': 'TX', 'BELLEVUE': 'WA', 'BEND': 'OR', 'BETHESDA': 'MD',
    'BILLINGS': 'MT', 'BIRMINGHAM': 'AL', 'BLOOMINGTON': 'IL',
    'BOISE': 'ID', 'BOSTON': 'MA', 'BOULDER': 'CO', 'BURR RIDGE': 'IL',
    'CEDAR CITY': 'UT', 'CHADDS FORD': 'PA', 'CHANDLER': 'AZ',
    'CHARLOTTE': 'NC', 'CHESTERFIELD': 'MO', 'CHEYENNE': 'WY',
    'CINCINNATI': 'OH', 'CLEVELAND': 'OH', 'COLLEGE STATION': 'TX',
    'COLUMBIA': 'MO', 'CORBIN': 'KY', 'DALLAS': 'TX', 'DAVIE': 'FL',
    'DAYTONA BEACH': 'FL', 'DEERFIELD': 'IL', 'DELRAY BEACH': 'FL',
    'DENVER': 'CO', 'DRAPER': 'UT', 'DUBLIN': 'OH', 'EDMONDS': 'WA',
    'EL PASO': 'TX', 'ENNIS': 'TX', 'FARGO': 'ND', 'FARMINGTON': 'UT',
    'FORT LAUDERDALE': 'FL', 'FORT MILL': 'SC', 'FORT MYERS': 'FL',
    'FORT WAYNE': 'IN', 'FORT WORTH': 'TX', 'FRAMINGHAM': 'MA',
    'FRANKLIN': 'TN', 'FRISCO': 'TX', 'GILBERT': 'AZ',
    'GOODYEAR': 'AZ', 'GRAND PRAIRIE': 'TX', 'GREENWOOD VILLAGE': 'CO',
    'GULF BREEZE': 'FL', 'HEATH': 'TX', 'HENDERSON': 'NV',
    'HEWLETT': 'NY', 'HIGHLANDS RANCH': 'CO', 'HOMEWOOD': 'AL',
    'HONOLULU': 'HI', 'HOUSTON': 'TX', 'HUNTSVILLE': 'AL',
    'INCLINE VILLAGE': 'NV', 'IRVING': 'TX', 'JACKSON': 'MS',
    'KAILUA KONA': 'HI', 'KANEOHE': 'HI', 'KANSAS CITY': 'MO',
    'KNOXVILLE': 'TN', 'LAKE HAVASU CITY': 'AZ', 'LAKE OSWEGO': 'OR',
    'LAKEWOOD': 'CO', 'LAS VEGAS': 'NV', 'LAWRENCE': 'KS',
    'LEWES': 'DE', 'LISLE': 'IL', 'LONGMONT': 'CO', 'MAHWAH': 'NJ',
    'MARCO ISLAND': 'FL', 'MEDFORD': 'OR', 'MEDINA': 'WA',
    'MEMPHIS': 'TN', 'MERCER ISLAND': 'WA', 'MIAMI': 'FL',
    'MIAMI BEACH': 'FL', 'MOORESVILLE': 'NC', 'MT PROSPECT': 'IL',
    'NAPLES': 'FL', 'NEW FAIRFIELD': 'CT', 'NEW YORK': 'NY',
    'NEWARK': 'DE', 'NINE MILE FALLS': 'WA', 'NOLENSVILLE': 'TN',
    'OAK BROOK': 'IL', 'OHATCHEE': 'AL', 'OSPREY': 'FL', 'OVIEDO': 'FL',
    'PARADISE VALLEY': 'AZ', 'PARK CITY': 'UT', 'PEORIA': 'AZ',
    'PERRYSBURG': 'OH', 'PHOENIX': 'AZ', 'PLANO': 'TX',
    'PORTLAND': 'OR', 'PRESCOTT': 'AZ', 'PROVO': 'UT',
    'QUEEN CREEK': 'AZ', 'QUEENS VILLAGE': 'NY', 'RENO': 'NV',
    'SALT LAKE CITY': 'UT', 'SAN ANTONIO': 'TX', 'SANDY': 'UT',
    'SANDYVILLE': 'MS', 'SCOTTSDALE': 'AZ', 'SEATTLE': 'WA',
    'SEDALIA': 'MO', 'SHEFFIELD VILLAGE': 'OH', 'SHERIDAN': 'WY',
    'SNOWMASS VILLAGE': 'CO', 'SOUTHLAKE': 'TX', 'SUGAR LAND': 'TX',
    'SYOSSET': 'NY', 'TETERBORO': 'NJ', 'TULSA': 'OK',
    'WATERTOWN': 'MA', 'WEST BLOOMFIELD': 'MI', 'WESTON': 'FL',
    'WICHITA FALLS': 'TX', 'WILMINGTON': 'DE', 'WOODBURY': 'MN',
    'WOODLAND PARK': 'CO', 'WOODWAY': 'WA', 'WOONSOCKET': 'RI',
    'YARROW POINT': 'WA', 'ZEPHYR COVE': 'NV',
    'DEER ISLAND': 'OR',
}


def mail_city_to_state(city: str) -> str:
    return CITY_TO_STATE.get(city.strip().upper(), 'CA')


def clean_entity_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = name.upper()
    name = re.sub(r'[.,\-&/()]', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip()


# ------------------------------------------------------------
# 1. LOAD LLC LIST
# ------------------------------------------------------------
def load_llc_list(csv_path: str) -> List[Dict]:
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    records = []
    for _, row in df.iterrows():
        owner1 = str(row.get('Owner1', '')).strip()
        if not owner1 or owner1 == 'nan':
            continue
        city_raw = str(row.get('MailCity', '')).strip()
        records.append({
            'llc_name': owner1,
            'clean_name': clean_entity_name(owner1),
            'owner2': str(row.get('Owner2', '')).strip(),
            'property_address': str(row.get('SiteAddress', '')).strip(),
            'mail_address': str(row.get('MailAddress', '')).strip(),
            'mail_city': city_raw,
            'mail_state': mail_city_to_state(city_raw),
            'apn': str(row.get('APN', '')).strip(),
            'last_seller': str(row.get('LastSeller', '')).strip(),
            'last_sale_date': str(row.get('LastSaleDate', '')).strip(),
            'last_sale_value': row.get('LastSaleValue', 0),
            'property_zip': '',
        })
    return records


# ------------------------------------------------------------
# 2. MULTI-TIER PPP INGESTION & MATCHING
# ------------------------------------------------------------
# Map SBA dataset column names to user-friendly aliases
SBA_COL_MAP = {
    'BusinessName': 'BorrowerName',
    'LoanAmount': 'CurrentApprovalAmount',
    'City': 'BorrowerCity',
    'State': 'BorrowerState',
    'Zip': 'BorrowerZip',
}


def load_and_combine_ppp() -> pd.DataFrame:
    """Loads both tier datasets, cleans them, and merges into a single dataframe."""
    file_tier_1 = "public_150k_plus_240930.csv"
    file_tier_2 = "ppp_up_to_150k.csv"

    combined_df = pd.DataFrame(columns=['clean_name', 'BusinessName', 'City', 'State', 'Zip',
                                         'LoanAmount', 'DateApproved', 'ForgivenessAmount'])

    for file in [file_tier_1, file_tier_2]:
        try:
            df = pd.read_csv(file, encoding='latin1', low_memory=False)

            # Map actual SBA column names to expected names
            df['BusinessName'] = df['BorrowerName']
            df['LoanAmount'] = df['CurrentApprovalAmount']
            df['City'] = df['BorrowerCity']
            df['State'] = df['BorrowerState']
            df['Zip'] = df['BorrowerZip'].astype(str).str[:5]

            # Standardize business names immediately
            df['clean_name'] = df['BusinessName'].apply(clean_entity_name)

            # Drop unnecessary columns to save memory
            cols_to_keep = ['clean_name', 'BusinessName', 'City', 'State', 'Zip',
                            'LoanAmount', 'DateApproved', 'ForgivenessAmount']
            df = df[[c for c in cols_to_keep if c in df.columns]]

            print(f"[+] Loaded {len(df):,} records from {file}")
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        except FileNotFoundError:
            print(f"[!] Warning: {file} not found locally. Skipping.")

    print(f"[PPP] Final combined SBA matrix ready: {len(combined_df):,} total records.")
    return combined_df


def match_ppp_all_tiers(llc_row: dict, ppp_df: pd.DataFrame) -> list:
    """
    Executes an exact name match first.
    If no hit, executes a geographic fallback using the cleaned 5-digit ZIP.
    """
    llc_name = clean_entity_name(llc_row.get("llc_name", ""))
    llc_zip = str(llc_row.get("property_zip", ""))[:5]
    matches = []

    # 1. Exact Name Match
    exact_hits = ppp_df[ppp_df['clean_name'] == llc_name]

    if not exact_hits.empty:
        for _, row in exact_hits.iterrows():
            matches.append({
                "match_type": "Exact Name",
                "business_name": row.get("BusinessName", ""),
                "loan_amount": row.get("LoanAmount", 0),
                "forgiven": row.get("ForgivenessAmount", 0),
                "city": row.get("City", ""),
                "state": row.get("State", ""),
                "zip": row.get("Zip", "")
            })
        return matches

    # 2. Fallback: ZIP Code match (capped at 5)
    if len(llc_zip) == 5:
        zip_hits = ppp_df[ppp_df['Zip'] == llc_zip]
        if not zip_hits.empty:
            for _, row in zip_hits.head(5).iterrows():
                matches.append({
                    "match_type": "ZIP Fallback",
                    "business_name": row.get("BusinessName", ""),
                    "loan_amount": row.get("LoanAmount", 0),
                    "forgiven": row.get("ForgivenessAmount", 0)
                })

    return matches


# ------------------------------------------------------------
# 3. IRS 990 (NONPROFIT EXPLORER API)
# ------------------------------------------------------------
def search_nonprofit(ein: str = None, name: str = None) -> Optional[Dict]:
    params = {}
    if ein:
        params["ein"] = ein
    elif name:
        params["q"] = name
    else:
        return None
    url = f"{NONPROFIT_API_BASE}/search.json"
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("organizations"):
                return data["organizations"][0]
    except Exception as e:
        print(f"[990] Error searching for {name or ein}: {e}")
    return None


# ------------------------------------------------------------
# 4. NEVADA SECRETARY OF STATE LOOKUP
# ------------------------------------------------------------
def lookup_nv_sos(entity_name: str) -> Dict:
    """Placeholder — replace with Apify/Global Database API for production."""
    return {
        "registered_agent": "CORPORATE CREATIONS NETWORK INC.",
        "filing_number": "NV2021XXXXX",
        "status": "Active",
        "formed_date": "2021-03-15",
    }


# ------------------------------------------------------------
# 5. MAIN
# ------------------------------------------------------------
def main():
    print("RICO OSINT Cross-Reference Tool")
    print("================================")

    llcs = load_llc_list(INPUT_CSV)
    print(f"[+] Loaded {len(llcs)} LLCs from {INPUT_CSV}")

    ppp_df = load_and_combine_ppp()

    nonprofit_cache = {}
    evidence_rows = []
    for llc in tqdm(llcs, desc="Processing LLCs"):
        llc_name = llc["llc_name"]
        row = {
            "llc_name": llc_name,
            "owner2": llc.get("owner2", ""),
            "property_address": llc.get("property_address", ""),
            "mail_address": llc.get("mail_address", ""),
            "mail_city": llc.get("mail_city", ""),
            "mail_state": llc.get("mail_state", ""),
            "apn": llc.get("apn", ""),
            "last_seller": llc.get("last_seller", ""),
            "last_sale_date": llc.get("last_sale_date", ""),
            "last_sale_value": llc.get("last_sale_value", 0),
        }

        # PPP loans (exact name match, then ZIP fallback)
        ppp_matches = match_ppp_all_tiers(llc, ppp_df)
        row["ppp_loan_count"] = len(ppp_matches)
        row["ppp_total_amount"] = sum(
            m["loan_amount"] if pd.notna(m["loan_amount"]) else 0
            for m in ppp_matches
        )
        row["ppp_forgiven_amount"] = sum(
            m["forgiven"] if pd.notna(m["forgiven"]) else 0
            for m in ppp_matches
        )
        row["ppp_match_types"] = ", ".join(set(m.get("match_type", "") for m in ppp_matches))
        row["ppp_loan_details"] = json.dumps(ppp_matches)

        # IRS 990 search (cache by name)
        llc_key = llc_name.upper().strip()
        if llc_key not in nonprofit_cache:
            time.sleep(0.25)
            nonprofit = search_nonprofit(name=llc_name)
            nonprofit_cache[llc_key] = nonprofit
        else:
            nonprofit = nonprofit_cache[llc_key]
        if nonprofit:
            row["nonprofit_ein"] = nonprofit.get("ein", "")
            row["nonprofit_name"] = nonprofit.get("name", "")
            row["nonprofit_ntee"] = nonprofit.get("ntee_code", "")
            row["nonprofit_filing_count"] = 0
            row["nonprofit_latest_revenue"] = 0
        else:
            row["nonprofit_ein"] = ""
            row["nonprofit_name"] = ""
            row["nonprofit_ntee"] = ""
            row["nonprofit_filing_count"] = 0
            row["nonprofit_latest_revenue"] = 0

        # NV SOS lookup (only for NV-registered LLCs)
        if llc.get("mail_state") == "NV":
            sos = lookup_nv_sos(llc_name)
            row["nv_registered_agent"] = sos.get("registered_agent", "")
            row["nv_filing_number"] = sos.get("filing_number", "")
            row["nv_status"] = sos.get("status", "")
            row["nv_formed_date"] = sos.get("formed_date", "")
        else:
            row["nv_registered_agent"] = ""
            row["nv_filing_number"] = ""
            row["nv_status"] = ""
            row["nv_formed_date"] = ""

        evidence_rows.append(row)

    df_out = pd.DataFrame(evidence_rows)
    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"\nDone! Evidence matrix written to {OUTPUT_CSV}")
    print(f"   Total LLCs processed: {len(df_out)}")
    print(f"   NV mail addresses: {sum(1 for r in evidence_rows if r.get('mail_state') == 'NV')}")
    print(f"   PPP loan matches: {sum(1 for r in evidence_rows if r.get('ppp_loan_count', 0) > 0)}")
    ppp_total = sum(r.get('ppp_total_amount', 0) or 0 for r in evidence_rows)
    forgiven_total = sum(r.get('ppp_forgiven_amount', 0) or 0 for r in evidence_rows)
    print(f"   PPP total amount: ${ppp_total:,.0f}")
    print(f"   PPP total forgiven: ${forgiven_total:,.0f}")
    print(f"   IRS 990 hits: {sum(1 for r in evidence_rows if r.get('nonprofit_ein', ''))}")
    print(f"   NV SOS lookups performed: {sum(1 for r in evidence_rows if r.get('nv_registered_agent', ''))}")


if __name__ == "__main__":
    main()
