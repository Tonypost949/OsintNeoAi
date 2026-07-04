#!/bin/bash
# Check if project ID is provided
if [ -z "$1" ]; then
  echo "Error: Please provide a Google Cloud Project ID."
  echo "Usage: ./setup.sh <YOUR_PROJECT_ID>"
  exit 1
fi

PROJECT_ID=$1

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Configuring GCP Auth..."
gcloud auth login
gcloud config set project "$PROJECT_ID"

echo "Bootstrapping database schema..."
bq query --use_legacy_sql=false --project_id="$PROJECT_ID" < bootstrap_db.sql

echo "Deploying to Cloud Run..."
gcloud run deploy osint-chat-ui-xxl \
  --source . \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_PROJECT_ID="$PROJECT_ID" \
  --project "$PROJECT_ID"

echo "Done. Your agent is live at the URL generated above."
