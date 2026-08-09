import os
from google.cloud import bigquery

# Initialize BQ Client
client = bigquery.Client()

cities = ['reno', 'spokane', 'phoenix', 'sacramento', 'san francisco', 'san diego']

markdown_content = "# NATIONWIDE PPP FRAUD HOLES AROUND SPRUNG STRUCTURES\n\n"
markdown_content += "The following are the largest 'virtual office' / 'drop' clusters in the cities where major Sprung structure Navigation Centers were forced into existence. The scammers harvest PII at the Sprung structures and register the PPP shell LLCs at these local drop addresses.\n\n"

for city in cities:
    markdown_content += f"## {city.upper()}\n"
    query = f"""
    SELECT BorrowerAddress, COUNT(*) as loan_count, SUM(CurrentApprovalAmount) as total_amount 
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k` 
    WHERE LOWER(BorrowerCity) = '{city}' 
    GROUP BY BorrowerAddress 
    HAVING loan_count > 10 
    ORDER BY loan_count DESC 
    LIMIT 10
    """
    
    try:
        query_job = client.query(query)
        results = query_job.result()
        
        markdown_content += "| Address | Loan Count | Total $ Siphoned |\n"
        markdown_content += "|---|---|---|\n"
        
        found = False
        for row in results:
            found = True
            address = row['BorrowerAddress']
            count = row['loan_count']
            amount = row['total_amount']
            markdown_content += f"| {address} | {count} | ${amount:,.2f} |\n"
            
        if not found:
            markdown_content += "*(No clusters > 10 found in up_to_150k)*\n"
    except Exception as e:
        markdown_content += f"Error querying: {e}\n"
    
    markdown_content += "\n"
    
out_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\33734c99-ad08-4e0f-a28a-c93f13b88bfe\NATIONWIDE_PPP_HOLES.md"
with open(out_path, "w") as f:
    f.write(markdown_content)
    
print("Successfully generated NATIONWIDE_PPP_HOLES.md")
