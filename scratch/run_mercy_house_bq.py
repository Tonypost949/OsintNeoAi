import json
from google.cloud import bigquery

client = bigquery.Client()

queries = {
    "mercy_house_loans": """
        SELECT
            BorrowerName,
            BorrowerAddress,
            BorrowerCity,
            BorrowerState,
            OriginatingLender,
            CurrentApprovalAmount,
            ForgivenessAmount
        FROM (
            SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, OriginatingLender, CurrentApprovalAmount, ForgivenessAmount
            FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
            UNION ALL
            SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, OriginatingLender, CurrentApprovalAmount, ForgivenessAmount
            FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
        )
        WHERE LOWER(BorrowerName) LIKE '%mercy house%'
    """,
    "zero_dollar_entities": """
        SELECT
            BorrowerName,
            BorrowerAddress,
            OriginatingLender,
            CurrentApprovalAmount,
            ForgivenessAmount
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
        WHERE LOWER(BorrowerName) IN (
            'pacific city hotel llc',
            'stewart industries llc',
            'newport llc',
            'drt llc',
            'lighthouse cafe llc',
            'incuplace llc',
            'rav llc',
            'the le family llc',
            'first highland llc'
        )
    """,
    "stewart_family_loans": """
        SELECT
            BorrowerName,
            OriginatingLender,
            CurrentApprovalAmount,
            ForgivenessAmount
        FROM (
            SELECT BorrowerName, OriginatingLender, CurrentApprovalAmount, ForgivenessAmount
            FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
            UNION ALL
            SELECT BorrowerName, OriginatingLender, CurrentApprovalAmount, ForgivenessAmount
            FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
        )
        WHERE LOWER(BorrowerName) LIKE '%stewart%' AND (LOWER(BorrowerName) LIKE '%josh%' OR LOWER(BorrowerName) LIKE '%brenda%')
    """
}

results = {}

for name, query in queries.items():
    try:
        job = client.query(query)
        rows = [dict(row.items()) for row in job.result()]
        results[name] = rows
    except Exception as e:
        results[name] = str(e)

with open(r"C:\osintneoai\scratch\bq_mercy_house_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
