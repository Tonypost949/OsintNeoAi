# Zero-Trust Cross-Cloud Architecture
**Azure-to-GCP Workload Identity Federation (WIF)**

To eliminate the catastrophic security risk of static JSON service account keys, the OSINT Ingestion Engine (hosted on Azure) communicates with the BigQuery Master Ledger (hosted on GCP) exclusively through OpenID Connect (OIDC) token exchange.

## Implementation Sequence

### 1. Provision the Azure Identity
Create a User-Assigned Managed Identity (or App Registration) specifically for the `OSINTNEOMAXX` backend in Azure Portal.
*   **Target:** Generates the unique Client ID and Object ID.

### 2. Build the GCP Identity Pool and OIDC Provider
Create a Workload Identity Pool in GCP and attach an OIDC Provider. 
*   **Issuer URL:** `https://sts.windows.net/{YOUR_AZURE_TENANT_ID}/`
*   **Verification:** `gcloud iam workload-identity-pools providers describe`

### 3. Configure Strict Attribute Mapping
Map incoming Azure token claims to GCP attributes to prevent spoofing.
*   **Mapping:** `google.subject` = `assertion.sub` (Azure Object ID)
*   **Condition:** Explicitly require the incoming token to match the specific Azure Client ID.

### 4. Bind the Service Account & BigQuery Roles
Create a dedicated GCP Service Account.
*   **Permissions:** Grant `BigQuery Data Editor` to the Service Account.
*   **Impersonation:** Grant `roles/iam.workloadIdentityUser` to the Workload Identity Pool user on this specific service account.

## Application Execution
GCP outputs a non-sensitive client configuration file. The Azure Python backend uses this file in conjunction with the Azure `DefaultAzureCredential` to transparently negotiate short-lived, identity-bound access tokens on the fly.
