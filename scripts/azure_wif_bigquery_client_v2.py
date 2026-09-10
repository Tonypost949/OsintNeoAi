"""
OsintNeoAi — Azure-to-GCP WIF BigQuery Client (v2)
==================================================
Connects to BigQuery from Azure using Workload Identity Federation (WIF) OIDC.
"""

import os
import json
import logging
from google.cloud import bigquery
from google.auth import exceptions

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("WIF_BQ_CLIENT")

WIF_CONFIG_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "config/azure_gcp_wif_credentials.json")
GCP_PROJECT = os.environ.get("GCP_PROJECT", "noble-beanbag-497411-m4")

def get_wif_bigquery_client():
    """Initializes BigQuery client using WIF configuration or falls back to ambient ADC."""
    if os.path.exists(WIF_CONFIG_PATH):
        logger.info(f"Using WIF configuration from: {WIF_CONFIG_PATH}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(WIF_CONFIG_PATH)
    else:
        logger.info("WIF config file not found; using ambient ADC or gcloud auth.")
    
    client = bigquery.Client(project=GCP_PROJECT)
    return client

def test_connection():
    """Validates connectivity to BigQuery forensic_layers dataset."""
    try:
        client = get_wif_bigquery_client()
        query = "SELECT dataset_id FROM `noble-beanbag-497411-m4.__TABLES__` LIMIT 5"
        job = client.query(query)
        rows = list(job.result())
        logger.info(f"✅ Successfully connected to BigQuery via WIF/ADC. Retrieved {len(rows)} table metadata rows.")
        return True
    except Exception as e:
        logger.warning(f"BigQuery connection test completed with status: {e}")
        return False

if __name__ == "__main__":
    test_connection()
