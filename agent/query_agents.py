from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("--- Query 1: Getting Agents for DRT, JEK, RAV ---")
query1 = """
SELECT Owner1, agent_of_service, principal_address, mailing_address
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%DRT%' 
   OR UPPER(Owner1) LIKE '%JEK%' 
   OR UPPER(Owner1) LIKE '%RAV%';
"""

try:
    results1 = client.query(query1).result()
    for row in results1:
        print(f"Owner1: {row.Owner1}")
        print(f"Agent: {row.agent_of_service}")
        print(f"Principal Address: {row.principal_address}")
        print(f"Mailing Address: {row.mailing_address}")
        print("-" * 40)
except Exception as e:
    print(f"Error in Query 1: {e}")

print("\n--- Query 2: Finding shared agents ---")
query2 = """
SELECT agent_of_service, COUNT(*) as count
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
WHERE agent_of_service IN (
    SELECT agent_of_service
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
    WHERE Owner1 IN ('DRT INVESTMENTS LLC', 'JEK INVESTMENTS LLC', 'RAV LLC')
)
AND agent_of_service IS NOT NULL
AND agent_of_service != ''
GROUP BY agent_of_service
ORDER BY COUNT(*) DESC;
"""

try:
    results2 = client.query(query2).result()
    for row in results2:
        print(f"Agent: {row.agent_of_service} | Count: {row.count}")
except Exception as e:
    print(f"Error in Query 2: {e}")
