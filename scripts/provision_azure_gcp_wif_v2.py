"""
OsintNeoAi — Azure-to-GCP Workload Identity Federation (WIF) Provisioner (v2)
=============================================================================
Implements Zero-Trust Cross-Cloud OIDC token exchange between Azure Managed
Identities / Entra ID and Google Cloud Workload Identity Pools (BigQuery access).
"""

import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("WIF_PROVISIONER")

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT", "noble-beanbag-497411-m4")
GCP_POOL_ID = "azure-osintneoai-pool"
GCP_PROVIDER_ID = "azure-entra-oidc-provider"
GCP_SERVICE_ACCOUNT_NAME = "azure-wif-bq-collector"
GCP_SERVICE_ACCOUNT_EMAIL = f"{GCP_SERVICE_ACCOUNT_NAME}@{GCP_PROJECT_ID}.iam.gserviceaccount.com"

# Azure Entra ID Tenant
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", "f055033f-83fb-4ae9-9c36-be48f0c86158")
AZURE_ISSUER_URL = f"https://sts.windows.net/{AZURE_TENANT_ID}/"

def generate_wif_gcloud_commands():
    """Generates the idempotent gcloud commands to configure GCP Workload Identity Pool."""
    commands = [
        # 1. Create Workload Identity Pool
        f"gcloud iam workload-identity-pools create {GCP_POOL_ID} "
        f"--project={GCP_PROJECT_ID} --location=global "
        f"--display-name='Azure OSINT Neo AI Workload Identity Pool'",

        # 2. Attach Azure OIDC Provider
        f"gcloud iam workload-identity-pools providers create-oidc {GCP_PROVIDER_ID} "
        f"--project={GCP_PROJECT_ID} --location=global "
        f"--workload-identity-pool={GCP_POOL_ID} "
        f"--issuer-uri='{AZURE_ISSUER_URL}' "
        f"--attribute-mapping='google.subject=assertion.sub,attribute.aud=assertion.aud,attribute.tid=assertion.tid' "
        f"--display-name='Azure Entra ID OIDC Provider'",

        # 3. Create Dedicated Service Account
        f"gcloud iam service-accounts create {GCP_SERVICE_ACCOUNT_NAME} "
        f"--project={GCP_PROJECT_ID} "
        f"--display-name='Azure Cross-Cloud BigQuery Data Collector'",

        # 4. Grant BigQuery Data Editor & Job User to Service Account
        f"gcloud projects add-iam-policy-binding {GCP_PROJECT_ID} "
        f"--member='serviceAccount:{GCP_SERVICE_ACCOUNT_EMAIL}' "
        f"--role='roles/bigquery.dataEditor'",
        f"gcloud projects add-iam-policy-binding {GCP_PROJECT_ID} "
        f"--member='serviceAccount:{GCP_SERVICE_ACCOUNT_EMAIL}' "
        f"--role='roles/bigquery.jobUser'",

        # 5. Allow Azure Workload Pool identities to impersonate the GCP Service Account
        f"gcloud iam service-accounts add-iam-policy-binding {GCP_SERVICE_ACCOUNT_EMAIL} "
        f"--project={GCP_PROJECT_ID} "
        f"--role='roles/iam.workloadIdentityUser' "
        f"--member='principalSet://iam.googleapis.com/projects/{GCP_PROJECT_ID}/locations/global/workloadIdentityPools/{GCP_POOL_ID}/*'"
    ]
    return commands

def create_wif_client_config(output_path="config/azure_gcp_wif_credentials.json"):
    """Generates the non-sensitive client configuration file for Azure Python clients."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    config = {
        "type": "external_account",
        "audience": f"//iam.googleapis.com/projects/{GCP_PROJECT_ID}/locations/global/workloadIdentityPools/{GCP_POOL_ID}/providers/{GCP_PROVIDER_ID}",
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "token_url": "https://sts.googleapis.com/v1/token",
        "credential_source": {
            "url": "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fiam.googleapis.com%2F",
            "headers": {
                "Metadata": "true"
            },
            "format": {
                "type": "json",
                "subject_token_field_name": "access_token"
            }
        },
        "service_account_impersonation_url": f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{GCP_SERVICE_ACCOUNT_EMAIL}:generateAccessToken"
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    logger.info(f"Generated non-sensitive WIF client configuration at: {output_path}")
    return output_path

if __name__ == "__main__":
    logger.info("Initializing Azure-to-GCP Workload Identity Federation (WIF) Configuration...")
    cmds = generate_wif_gcloud_commands()
    config_file = create_wif_client_config()
    print("\n--- GCP WIF PROVISIONING INSTRUCTIONS ---")
    for idx, c in enumerate(cmds, 1):
        print(f"[{idx}] {c}")
    print(f"\n[+] WIF Client Config saved to: {config_file}")
