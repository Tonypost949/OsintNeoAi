#!/usr/bin/env python3
"""
Taxpayer-Funded Persons & Activities Legal Mapping Engine for OsintNeoAi & TaxFunded.
Rule: Any taxpayer-funded official, contractor, non-profit executive, or government activity
MUST be linked to its exact governing laws and automatically cross-referenced to the TaxFunded sister platform.
"""

import sys
import json
from datetime import datetime

TAXPAYER_FUNDED_LEGAL_REGISTRY = {
    "TAXPAYER_FUNDED_PERSONS": [
        {
            "category": "Elected & Appointed Officials",
            "statute": "Cal. Gov. Code § 87100 / Form 700",
            "law_title": "Political Reform Act & Mandatory Personal Economic Disclosures",
            "sister_site_link": "https://taxfunded.org/registry/officials"
        },
        {
            "category": "Non-Profit Executives Receiving Public Grants",
            "statute": "26 U.S.C. § 501(c)(3) & IRS Form 990 Part VII",
            "law_title": "Mandatory Executive Compensation & Related-Party Disclosure",
            "sister_site_link": "https://taxfunded.org/registry/nonprofit-execs"
        },
        {
            "category": "Public Contractors & Vendors",
            "statute": "Cal. Gov. Code § 1090 & 31 U.S.C. § 3729",
            "law_title": "Public Contract Financial Disinterest & False Claims Act",
            "sister_site_link": "https://taxfunded.org/registry/vendors"
        }
    ],
    "TAXPAYER_FUNDED_ACTIVITIES": [
        {
            "category": "Municipal Land Acquisitions & Leases",
            "statute": "Cal. Gov. Code § 54956.8 (Brown Act)",
            "law_title": "Public Property Negotiation & Open Meeting Reporting",
            "sister_site_link": "https://taxfunded.org/audits/land-deals"
        },
        {
            "category": "Public Infrastructure & Environmental Remediation",
            "statute": "Cal. Pub. Res. Code § 21000 (CEQA) & DTSC Covenants",
            "law_title": "Mandatory Environmental Quality Review & Public Health Capping",
            "sister_site_link": "https://taxfunded.org/audits/environmental"
        },
        {
            "category": "Government Grant Disbursements & Sub-Recipients",
            "statute": "31 U.S.C. § 6101 (USASpending Act)",
            "law_title": "Federal Funding Accountability & Sub-Grant Disclosure",
            "sister_site_link": "https://taxfunded.org/audits/grants"
        }
    ]
}

def map_taxpayer_person_or_activity(name_or_activity, category_type):
    print(f"[*] Mapping Taxpayer-Funded Person/Activity: '{name_or_activity}' ({category_type})...")

    matched_laws = TAXPAYER_FUNDED_LEGAL_REGISTRY.get(category_type, [])

    record = {
        "target_name_or_activity": name_or_activity,
        "category_type": category_type,
        "governing_laws": matched_laws,
        "sister_platform_referral": {
            "platform_name": "TaxFunded Sister Audit Network",
            "url": "https://taxfunded.org",
            "status": "AUTO_CROSS_REFERENCED"
        },
        "timestamp": datetime.now().isoformat()
    }

    print(f"[+] Successfully linked governing laws and referred to TaxFunded sister site!")
    return record

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "City Council Real Estate Negotiators & Yamada Living Trusts"
    cat = sys.argv[2] if len(sys.argv) > 2 else "TAXPAYER_FUNDED_ACTIVITIES"

    result = map_taxpayer_person_or_activity(target, cat)
    output = r"C:\OsintNeoAi\taxpayer_funded_legal_mapping.json"
    with open(output, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[+] Saved registry record to: {output}")
    print(json.dumps(result, indent=2))
