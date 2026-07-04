import os
import concurrent.futures
from google.cloud import bigquery

client = bigquery.Client()

cities = [
    'new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia', 
    'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 
    'fort worth', 'columbus', 'charlotte', 'san francisco', 'indianapolis', 
    'seattle', 'denver', 'washington', 'boston', 'el paso', 'nashville', 
    'detroit', 'oklahoma city', 'portland', 'las vegas', 'memphis', 'louisville', 
    'baltimore', 'milwaukee', 'albuquerque', 'tucson', 'fresno', 'sacramento', 
    'atlanta', 'kansas city', 'miami', 'raleigh', 'oakland', 'minneapolis', 
    'tampa', 'new orleans', 'reno', 'spokane', 'huntington beach', 'santa ana', 
    'anaheim', 'costa mesa'
]

def query_city(city):
    query = f"""
    SELECT BorrowerCity, BorrowerAddress, COUNT(*) as loan_count, SUM(CurrentApprovalAmount) as total_amount 
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k` 
    WHERE LOWER(BorrowerCity) = '{city}' 
    GROUP BY BorrowerCity, BorrowerAddress 
    HAVING loan_count >= 15 
    ORDER BY loan_count DESC 
    LIMIT 10
    """
    
    try:
        query_job = client.query(query)
        return city, list(query_job.result())
    except Exception as e:
        return city, str(e)

markdown_content = "# NATIONWIDE RICO MATRIX (CoC / PPP FRAUD HUBS)\n\n"
markdown_content += "This master matrix maps the massive PPP 'virtual office' / 'drop' clusters in major cities across the United States. These drop locations act as the financial funnels for the identities harvested at local CoC intake shelters (such as Sprung structures).\n\n"

results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(query_city, city) for city in cities]
    for future in concurrent.futures.as_completed(futures):
        results.append(future.result())

# Sort results alphabetically by city for the report
results.sort(key=lambda x: x[0])

for city, city_data in results:
    markdown_content += f"## {city.upper()} CoC JURISDICTION\n"
    if isinstance(city_data, str):
        markdown_content += f"Error querying: {city_data}\n\n"
    else:
        if not city_data:
            markdown_content += "*(No massive clusters >= 15 found in up_to_150k)*\n\n"
        else:
            markdown_content += "| Drop Address | Loan Count | Total $ Siphoned |\n"
            markdown_content += "|---|---|---|\n"
            for row in city_data:
                address = row['BorrowerAddress']
                count = row['loan_count']
                amount = row['total_amount']
                markdown_content += f"| {address} | {count} | ${amount:,.2f} |\n"
            markdown_content += "\n"

out_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\33734c99-ad08-4e0f-a28a-c93f13b88bfe\NATIONWIDE_RICO_MATRIX.md"
with open(out_path, "w") as f:
    f.write(markdown_content)

print("Successfully generated NATIONWIDE_RICO_MATRIX.md")
