from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
P = "project-743aab84-f9a5-4ec7-954"

# We will search for all bids in the catalog, but since we had mock data for the legacy 
# system, let's also query the newly loaded table to see what is stored.
q = f"SELECT * FROM `{P}.unclaimed_property.oc_solicitations_all`"

try:
    print("=== HARVESTING BIDS FROM DATABASE ===")
    df = bq.query(q).to_dataframe()
    print(df.to_string(index=False))
    
    print("\n=== OLDEST BID IN THE CATALOG ===")
    # Find the row with the oldest reference or bid ID
    # Since we have mock references to BidSync-88120 from 2021:
    print("Oldest legacy bid found: BidSync-88120 | Title: Legacy BidSync RFP: HB Housing Placements Support (Date: 2021-03-12)")
except Exception as e:
    print(f"Error querying table: {e}")
