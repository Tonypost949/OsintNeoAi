import urllib.request
import json
import ssl
import pandas as pd
from google.cloud import bigquery

def harvest_oc_procurement():
    # County of Orange, CA OpenGov portal identifier is 'ocgov'
    # We query the standard OpenGov public portal API for active solicitations
    url = "https://procurement.opengov.com/api/v1/portals/ocgov/solicitations?page=1&per_page=100&status=active"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print("Connecting to Orange County OpenGov Procurement API...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=20) as response:
            data = json.loads(response.read().decode('utf-8'))
            solicitations = data.get("data", [])
            print(f"Found {len(solicitations)} active solicitations/bids.")
            
            if not solicitations:
                print("No active bids returned.")
                return
                
            # Parse key fields: ID, title, status, open/close dates, category, and document links
            parsed_bids = []
            for s in solicitations:
                bid_id = s.get("id")
                attributes = s.get("attributes", {})
                title = attributes.get("title")
                status = attributes.get("status")
                bid_number = attributes.get("solicitation_number")
                released_at = attributes.get("released_at")
                closes_at = attributes.get("closes_at")
                
                # Fetch attachments details if available
                # OpenGov embeds document URLs in the details/attachments block
                documents = attributes.get("documents", [])
                doc_links = [doc.get("url") for doc in documents if doc.get("url")]
                
                parsed_bids.append({
                    "bid_id": str(bid_id),
                    "bid_number": str(bid_number),
                    "title": str(title),
                    "status": str(status),
                    "released_date": str(released_at),
                    "closing_date": str(closes_at),
                    "attachment_urls": ", ".join(doc_links) if doc_links else "None"
                })
                
            df = pd.DataFrame(parsed_bids)
            print("Preview of parsed OC bids:")
            print(df.head(5).to_string())
            
            # Ingest to BigQuery
            bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
            table_id = "project-743aab84-f9a5-4ec7-954.unclaimed_property.oc_procurement_bids"
            
            print(f"Loading {len(df)} bids into BigQuery table {table_id}...")
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
            )
            
            job = bq.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()
            print(f"✅ Successfully loaded Orange County bids into BigQuery!")
            
    except Exception as e:
        print(f"Error harvesting OC procurement: {e}")

if __name__ == "__main__":
    harvest_oc_procurement()
