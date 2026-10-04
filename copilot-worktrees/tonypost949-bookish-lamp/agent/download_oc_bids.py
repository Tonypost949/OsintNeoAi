import urllib.request
import json
import ssl
from google.cloud import bigquery
import os

# Orange County publishes active RFP/bids and procurement histories on the OC Procurement portal.
# We will download active bids and attachments, and ingest bid data into BigQuery.

def download_oc_bids():
    # Orange County procurement data endpoint
    url = "https://www.procurement.ocgov.com/api/bids" 
    # We will search the web or index to locate the direct open-data download link for OC procurement/bids.
    print("Preparing to harvest Orange County bids and attachments...")

download_oc_bids()
