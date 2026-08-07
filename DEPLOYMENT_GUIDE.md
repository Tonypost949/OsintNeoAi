# OsintNeoAi - Complete Deployment Guide

This guide will help you deploy OsintNeoAi across Google Cloud, GitHub Actions, and Colab.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Workflow                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Colab      │  │  Local Dev   │  │  GitHub Web  │       │
│  │  Notebooks   │  │  (Optional)  │  │   Editor     │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │               │
│         └──────────────────┼──────────────────┘               │
│                            │                                  │
│                     GitHub Repository                         │
│                   (auto-sync on push)                         │
│                            │                                  │
│         ┌──────────────────┼──────────────────┐              │
│         │                  │                  │              │
│    ┌────▼────┐        ┌────▼────┐       ┌────▼────┐         │
│    │ GitHub  │        │ GitHub  │       │ GitHub  │         │
│    │ Actions │        │ Actions │       │ Actions │         │
│    │ (Deploy)│        │(Auto-   │       │ (Colab) │         │
│    │         │        │commit)  │       │         │         │
│    └────┬────┘        └────┬────┘       └────┬────┘         │
│         │                  │                  │              │
│    ┌────▼────────┐    ┌────▼────┐       ┌────▼────┐         │
│    │Google Cloud │    │Schedule: │       │  Upload │         │
│    │   Run       │    │ Results  │       │  to GDr │         │
│    │             │    │Auto-push │       │         │         │
│    └────┬────────┘    └────┬────┘       └────┬────┘         │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                    GitHub (Store Results)                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Google AI Pro Account** ✅ (You have this)
2. **GitHub Account** ✅ (You have this)
3. **Google Cloud Project** (Free tier available)
4. **Gemini API Key** (Free tier: 60 requests/minute)

---

## Step 1: Set Up Google Cloud Project

### 1.1 Create a Google Cloud Project

```bash
# Visit: https://console.cloud.google.com
# Create a new project: "OsintNeoAi"
PROJECT_ID="project-743aab84-f9a5-4ec7-954"
REGION="us-central1"
```

### 1.2 Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable scheduler.googleapis.com
gcloud services enable container-registry.googleapis.com
gcloud services enable logging.googleapis.com
```

### 1.3 Create Service Account

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployer"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/scheduler.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

---

## Step 2: Configure GitHub Secrets

Go to: `https://github.com/Tonypost949/OsintNeoAi/settings/secrets/actions`

Add these secrets:

```
GEMINI_API_KEY = [Your API key from https://aistudio.google.com/app/apikey]
GCP_PROJECT_ID = project-743aab84-f9a5-4ec7-954
WIF_PROVIDER = [Generated in Step 3]
WIF_SERVICE_ACCOUNT = github-actions@project-743aab84-f9a5-4ec7-954.iam.gserviceaccount.com
GOOGLE_CREDENTIALS_JSON = [Generated in Step 3]
```

---

## Step 3: Set Up Workload Identity Federation (GitHub → GCP)

```bash
# Enable required services
gcloud services enable iap.googleapis.com
gcloud services enable sts.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# Create Workload Identity Pool
gcloud iam workload-identity-pools create "github" \
  --project=$PROJECT_ID \
  --location="global" \
  --display-name="GitHub Actions" \
  --disabled=false

# Get the pool resource name
WORKLOAD_IDENTITY_POOL_ID=$(gcloud iam workload-identity-pools describe "github" \
  --project=$PROJECT_ID \
  --location="global" \
  --format='value(name)')

# Create identity provider
gcloud iam workload-identity-pools providers create-oidc "github" \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github" \
  --display-name="GitHub" \
  --attribute-mapping="google.subject=assertion.sub,assertion.aud=assertion.aud,assertion.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-condition="assertion.aud == 'https://github.com/Tonypost949'" \
  --disabled=false

# Create service account mapping
gcloud iam service-accounts add-iam-policy-binding \
  github-actions@${PROJECT_ID}.iam.gserviceaccount.com \
  --project=$PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/YOUR_PROJECT_NUMBER/locations/global/workloadIdentityPools/github/attribute.repository/Tonypost949/OsintNeoAi"

# Get WIF_PROVIDER value for GitHub secrets
echo "WIF_PROVIDER = projects/YOUR_PROJECT_NUMBER/locations/global/workloadIdentityPools/github/providers/github"
```

---

## Step 4: Deploy to Google Cloud Run

### 4.1 Manual Deployment (First Time)

```bash
# From your repo directory
cd Tonypost949/OsintNeoAi

# Build Docker image
docker build -t gcr.io/$PROJECT_ID/osint-neo-ai:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/osint-neo-ai:latest

# Deploy to Cloud Run
gcloud run deploy osint-neo-ai \
  --image gcr.io/$PROJECT_ID/osint-neo-ai:latest \
  --platform managed \
  --region $REGION \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,GCP_PROJECT_ID=$PROJECT_ID \
  --allow-unauthenticated
```

### 4.2 Automatic Deployment via GitHub Actions

Push to main branch:
```bash
git push origin main
```

The workflow `.github/workflows/deploy-google-cloud.yml` will automatically:
1. Build Docker image
2. Push to GCR
3. Deploy to Cloud Run
4. Set up Cloud Scheduler jobs
5. Auto-commit results back to GitHub

---

## Step 5: Set Up Periodic Jobs

### 5.1 Create Cloud Scheduler Jobs

```bash
# OSINT collection every 4 hours
gcloud scheduler jobs create http osint-data-collection \
  --location=$REGION \
  --schedule="0 */4 * * *" \
  --uri="https://osint-neo-ai-${REGION}.a.run.app/collect" \
  --http-method=POST \
  --oidc-service-account-email=github-actions@${PROJECT_ID}.iam.gserviceaccount.com \
  --oidc-token-audience="https://osint-neo-ai-${REGION}.a.run.app"

# Entity resolution every 12 hours
gcloud scheduler jobs create http osint-entity-resolution \
  --location=$REGION \
  --schedule="0 */12 * * *" \
  --uri="https://osint-neo-ai-${REGION}.a.run.app/resolve" \
  --http-method=POST \
  --oidc-service-account-email=github-actions@${PROJECT_ID}.iam.gserviceaccount.com \
  --oidc-token-audience="https://osint-neo-ai-${REGION}.a.run.app"

# Check scheduled jobs
gcloud scheduler jobs list --location=$REGION
```

---

## Step 6: Google Colab Integration

### 6.1 Create Colab Notebook

1. Go to: https://colab.research.google.com
2. Create new notebook: `OsintNeoAi-Dev.ipynb`
3. Add this setup cell:

```python
# Cell 1: Setup and clone repo
!git clone https://github.com/Tonypost949/OsintNeoAi.git
%cd OsintNeoAi

# Install dependencies
!pip install -q -r requirements.txt

# Set API key (you'll be prompted)
import os
from google.colab import userdata
GEMINI_API_KEY = userdata.get('GEMINI_API_KEY')
os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY
```

4. Add your analysis cells
5. Save to Google Drive: `Colab Notebooks/OsintNeoAi`

### 6.2 Run from Colab

```python
# Cell 2: Import and run
from main import OsintNeoAi

osint = OsintNeoAi()
results = osint.collect()
print(results)

# Auto-push results back to GitHub
!git config user.name "Colab Bot"
!git config user.email "colab@research.google.com"
!git add -A
!git commit -m "Results from Colab - $(date)"
!git push
```

---

## Step 7: Auto-Commit Workflow

The workflow `.github/workflows/auto-commit.yml` runs hourly and:

1. ✅ Checks out latest code
2. ✅ Runs OSINT collection
3. ✅ Saves results to `results/`
4. ✅ Auto-commits and pushes to GitHub
5. ✅ Creates alerts if anything fails

---

## Step 8: Monitor Your Deployments

### View Cloud Run Logs

```bash
gcloud run logs read osint-neo-ai --region=$REGION --limit 50
```

### View Cloud Scheduler Jobs

```bash
gcloud scheduler jobs list --location=$REGION
gcloud scheduler jobs describe osint-data-collection --location=$REGION
```

### View GitHub Actions

https://github.com/Tonypost949/OsintNeoAi/actions

### View Results in GitHub

https://github.com/Tonypost949/OsintNeoAi/tree/main/results

---

## Estimated Costs

| Service | Free Tier | Cost |
|---------|-----------|------|
| **Cloud Run** | 2M requests/month, 360K compute hours | ~$0.00 (in free tier) |
| **Cloud Scheduler** | 3 free jobs | $0.00 |
| **Gemini API** | 60 requests/minute | $0.00 (free tier) |
| **Colab** | Unlimited | $0.00 |
| **GitHub Actions** | 2,000 minutes/month | $0.00 (public repo) |
| **Total** | | **$0.00** ✅ |

---

## Troubleshooting

### Issue: "Cloud Run deployment fails"
```bash
# Check Cloud Build logs
gcloud builds log [BUILD_ID] --stream
```

### Issue: "Scheduler job not triggering"
```bash
# Check job execution history
gcloud scheduler jobs describe osint-data-collection --location=$REGION
gcloud scheduler jobs run osint-data-collection --location=$REGION
```

### Issue: "Gemini API rate limit"
- Add exponential backoff in `main.py`
- Increase request timeout
- Use batch processing

### Issue: "Git push fails in workflow"
```bash
# Verify token has write access
git remote set-url origin https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/Tonypost949/OsintNeoAi.git
```

---

## Next Steps

1. ✅ Complete steps 1-7 above
2. ✅ Test locally: `python main.py --mode collect`
3. ✅ Push to GitHub and watch workflows run
4. ✅ Monitor Cloud Run and Scheduler jobs
5. ✅ Access Colab notebooks for interactive analysis

---

## Support & Resources

- **Google Cloud Documentation**: https://cloud.google.com/docs
- **Gemini API Docs**: https://ai.google.dev/
- **GitHub Actions**: https://docs.github.com/en/actions
- **Google Colab**: https://colab.research.google.com/

---

**Your setup is now production-grade and will never freeze again!** 🚀
