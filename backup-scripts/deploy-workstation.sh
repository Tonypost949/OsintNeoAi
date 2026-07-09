#!/bin/bash
set -euo pipefail

PROJECT_ID="project-743aab84-f9a5-4ec7-954"
REGION="us-central1"
CLUSTER="migrated-home-cluster"
CONFIG="migrated-home-config"
WS_NAME="main-workstation"

gcloud config set project "$PROJECT_ID"

echo "=== ENABLING APIS ==="
gcloud services enable workstations.googleapis.com compute.googleapis.com

echo "=== CREATING VPC ==="
gcloud compute networks create migration-vpc --subnet-mode=custom 2>/dev/null || true
gcloud compute networks subnets create migration-subnet \
  --network=migration-vpc --range=10.0.0.0/24 --region="$REGION" \
  --enable-private-ip-google-access 2>/dev/null || true

echo "=== SETTING UP NAT ==="
gcloud compute routers create migration-router \
  --network=migration-vpc --region="$REGION" 2>/dev/null || true
gcloud compute routers nats create migration-nat \
  --router=migration-router --region="$REGION" \
  --nat-all-subnet-ip-ranges --auto-allocate-nat-external-ips 2>/dev/null || true

echo "=== CREATING WORKSTATION CLUSTER ==="
gcloud workstations clusters create "$CLUSTER" \
  --region="$REGION" --network=migration-vpc --subnetwork=migration-subnet 2>/dev/null || true

echo "=== CREATING WORKSTATION CONFIG ==="
gcloud workstations configs create "$CONFIG" \
  --cluster="$CLUSTER" --region="$REGION" \
  --machine-type=e2-standard-4 \
  --pd-disk-type=pd-ssd --pd-disk-size=100 \
  --container-image=us-central1-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest \
  --idle-timeout=7200s --running-timeout=86400s 2>/dev/null || true

echo "=== CREATING WORKSTATION ==="
gcloud workstations create "$WS_NAME" \
  --cluster="$CLUSTER" --config="$CONFIG" --region="$REGION" 2>/dev/null || true

echo "=== GRANTING ACCESS ==="
echo "Add users: gcloud workstations add-iam-policy-binding ..."

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo "Start: gcloud workstations start $WS_NAME --cluster=$CLUSTER --config=$CONFIG --region=$REGION"
echo "URL: https://console.cloud.google.com/workstations/workstation/$REGION/$CLUSTER/$CONFIG/$WS_NAME?project=$PROJECT_ID"
