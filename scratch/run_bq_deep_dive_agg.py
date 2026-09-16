import json
from google.cloud import bigquery

client = bigquery.Client()

queries = {
    "maricopa_aggregate": """
        SELECT
            OriginatingLender,
            COUNT(*) as loan_count,
            SUM(CurrentApprovalAmount) as total_approved,
            SUM(ForgivenessAmount) as total_forgiven
        FROM (
            SELECT OriginatingLender, CurrentApprovalAmount, ForgivenessAmount, BorrowerCity, ProjectCountyName
            FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
            UNION ALL
            SELECT OriginatingLender, CurrentApprovalAmount, ForgivenessAmount, BorrowerCity, ProjectCountyName
            FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
        )
        WHERE (LOWER(BorrowerCity) = 'maricopa' OR LOWER(ProjectCountyName) = 'maricopa')
          AND (LOWER(OriginatingLender) LIKE '%harvest small business%' OR LOWER(OriginatingLender) LIKE '%jpmorgan%')
        GROUP BY OriginatingLender
    """,
    "shell_factory_11770_warner_agg": """
        SELECT OriginatingLender, COUNT(*) as loan_count, SUM(CurrentApprovalAmount) as total_approved
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
        WHERE LOWER(BorrowerAddress) LIKE '%11770 warner%'
        GROUP BY OriginatingLender
    """,
    "shell_factory_newport_agg": """
        SELECT OriginatingLender, COUNT(*) as loan_count, SUM(CurrentApprovalAmount) as total_approved
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
        WHERE LOWER(BorrowerAddress) LIKE '%220 newport center%'
           OR LOWER(BorrowerAddress) LIKE '%620 newport center%'
        GROUP BY OriginatingLender
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

with open(r"C:\osintneoai\scratch\bq_deep_dive_agg.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
