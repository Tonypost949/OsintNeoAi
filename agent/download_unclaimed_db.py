import urllib.request
import json
import ssl
from google.cloud import bigquery

# The CA State Controller publishes raw unclaimed property data exports.
# We will download the official CSV dataset and load it into a new table 
# 'unclaimed_property.ca_unclaimed_raw' in BigQuery.
# Since we need to pull the actual CA controller raw files, let's locate the public datasets first.

def download_and_ingest_unclaimed():
    bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
    
    # Target table
    table_id = "project-743aab84-f9a5-4ec7-954.unclaimed_property.ca_unclaimed_raw"
    
    # We will search the web or public mirrors for the direct download link 
    # of the California unclaimed property raw database dumps (CSV/JSON/ZIP).
    # Many state agencies upload this to open data mirrors or FTP.
    # Let's search for the files.

download_and_ingest_unclaimed()
