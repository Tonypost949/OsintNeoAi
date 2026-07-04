#!/bin/bash
# setup_wif.sh — Run this in Cloud Shell or local gcloud
# Sets up Workload Identity Federation for GitHub Actions → GCP

PROJECT_ID="hardy-order-496117-p3"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
REPO="Tonypost949/OsintNeoAi"

echo "Project: $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"
echo "Repo: $REPO"

# 1. Enable services
gcloud services enable iamcredentials.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# 2. Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions" \
  --project=$PROJECT_ID || echo "SA already exists"

# 3. Create Workload Identity Pool
gcloud iam workload-identity-pools create "github" \
  --project=$PROJECT_ID \
  --location="global" \
  --display-name="GitHub Actions" \
  --disabled=false || echo "Pool already exists"

# 4. Create OIDC Provider
gcloud iam workload-identity-pools providers create-oidc "github" \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github" \
  --display-name="GitHub" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-condition="assertion.repository_owner == 'Tonypost949'" \
  --disabled=false || echo "Provider already exists"

# 5. Grant WIF access to SA
gcloud iam service-accounts add-iam-policy-binding \
  github-actions@${PROJECT_ID}.iam.gserviceaccount.com \
  --project=$PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github/attribute.repository/${REPO}"

# 6. Grant GCP roles to SA
for ROLE in roles/run.admin roles/bigquery.dataEditor roles/bigquery.jobUser roles/storage.admin roles/scheduler.admin; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="$ROLE"
done

# 7. Output secrets
echo ""
echo "================================================"
echo "Add these to GitHub Secrets:"
echo "================================================"
echo ""
echo "WIF_PROVIDER:"
echo "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github/providers/github"
echo ""
echo "GCP_PROJECT:"
echo "$PROJECT_ID"
echo ""
echo "WIF_SERVICE_ACCOUNT:"
echo "github-actions@${PROJECT_ID}.iam.gserviceaccount.com"
echo ""
echo "================================================"
