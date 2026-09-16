import json
from google.cloud import bigquery

client = bigquery.Client()

queries = {
    "harvest_volume": """
        SELECT
            OriginatingLender,
            ServicingLenderName,
            COUNT(*) as loan_count,
            SUM(CurrentApprovalAmount) as total_approved,
            SUM(ForgivenessAmount) as total_forgiven,
            SUM(ForgivenessAmount) - SUM(CurrentApprovalAmount) as total_over_forgiven
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
        WHERE LOWER(OriginatingLender) LIKE '%harvest small business%'
           OR LOWER(ServicingLenderName) LIKE '%harvest small business%'
        GROUP BY OriginatingLender, ServicingLenderName
    """,
    "jpmorgan_volume": """
        SELECT
            OriginatingLender,
            ServicingLenderName,
            COUNT(*) as loan_count,
            SUM(CurrentApprovalAmount) as total_approved,
            SUM(ForgivenessAmount) as total_forgiven,
            SUM(ForgivenessAmount) - SUM(CurrentApprovalAmount) as total_over_forgiven
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
        WHERE LOWER(OriginatingLender) LIKE '%jpmorgan%'
           OR LOWER(ServicingLenderName) LIKE '%jpmorgan%'
        GROUP BY OriginatingLender, ServicingLenderName
    """,
    "maricopa_harvest": """
        SELECT
            BorrowerName,
            BorrowerCity,
            BorrowerState,
            BorrowerZip,
            CurrentApprovalAmount,
            ForgivenessAmount,
            OriginatingLender
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
        WHERE (LOWER(BorrowerCity) = 'maricopa' OR LOWER(ProjectCountyName) = 'maricopa')
          AND (LOWER(OriginatingLender) LIKE '%harvest small business%' OR LOWER(OriginatingLender) LIKE '%jpmorgan%')
        ORDER BY CurrentApprovalAmount DESC
        LIMIT 100
    """,
    "maricopa_jpmorgan_under_150k": """
        SELECT
            BorrowerName,
            BorrowerCity,
            BorrowerState,
            CurrentApprovalAmount,
            ForgivenessAmount,
            OriginatingLender
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
        WHERE (LOWER(BorrowerCity) = 'maricopa' OR LOWER(ProjectCountyName) = 'maricopa')
          AND (LOWER(OriginatingLender) LIKE '%harvest small business%' OR LOWER(OriginatingLender) LIKE '%jpmorgan%')
        ORDER BY CurrentApprovalAmount DESC
        LIMIT 100
    """,
    "shell_factory_11770_warner": """
        SELECT
            BorrowerName,
            BorrowerAddress,
            OriginatingLender,
            CurrentApprovalAmount,
            ForgivenessAmount
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
        WHERE LOWER(BorrowerAddress) LIKE '%11770 warner%'
    """,
    "shell_factory_newport": """
        SELECT
            BorrowerName,
            BorrowerAddress,
            OriginatingLender,
            CurrentApprovalAmount,
            ForgivenessAmount
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
        WHERE LOWER(BorrowerAddress) LIKE '%220 newport center%'
           OR LOWER(BorrowerAddress) LIKE '%620 newport center%'
    """
}

results = {}

for name, query in queries.items():
    print(f"Running query: {name}")
    try:
        job = client.query(query)
        rows = [dict(row.items()) for row in job.result()]
        results[name] = rows
        print(f"  -> Got {len(rows)} rows.")
    except Exception as e:
        print(f"  -> ERROR: {e}")
        results[name] = str(e)

with open(r"C:\osintneoai\scratch\bq_deep_dive_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("Saved to bq_deep_dive_results.json")
