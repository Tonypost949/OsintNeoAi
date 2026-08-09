# OSINTNeoAiXL: Database Extraction Terminal 🕵️‍♂️

OSINTNeoAiXL is a production-grade, self-contained open-source Open Source Intelligence (OSINT) web portal designed to extract and audit municipal, environmental, and corporate contract anomalies across the United States.

## 🔗 Live Application
The live instance of this application is hosted publicly on Google Cloud Run:
👉 **[https://osint-chat-ui-xxl-941890989638.us-west1.run.app](https://osint-chat-ui-xxl-941890989638.us-west1.run.app)**

---

## 🛠️ Tech Stack & Architecture
- **Web UI**: Streamlit (Python)
- **Database**: Google BigQuery
- **Deployment**: Google Cloud Run (Dockerized Container)
- **Container Registry**: Artifact Registry

---

## 🚀 One-Click Deployment (Turn-Key)

To deploy your own instance of the extraction terminal to your own Google Cloud account in seconds:

1. **Fork this repository.**
2. **Execute the Setup Script**:
   Run the following terminal command, replacing `YOUR_PROJECT_ID` with your actual Google Cloud Project ID:
   ```bash
   bash setup.sh YOUR_PROJECT_ID
   ```
3. **Your Instance is now Live!** The script will install dependencies, authenticate with your GCP account, and automatically deploy the Dockerized container to Cloud Run.

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/OSINTNeoAiJun/OSINTNeoAiXXL.git
cd OSINTNeoAiXXL
```

### 2. Configure Environment Variables
Export your Google Cloud credentials and project ID before running:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
export GOOGLE_PROJECT_ID="your-gcp-project-id"
```

### 3. Install Dependencies & Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔄 Automated CI/CD Deployment

This repository includes a GitHub Action workflow located in `.github/workflows/deploy.yml`. 

To configure automatic deployment on every push to the `main` branch:
1. Go to your GitHub Repository **Settings** -> **Secrets and variables** -> **Actions**.
2. Add a new repository secret named **`GCP_SA_KEY`** containing the JSON key file of your Google Cloud Service Account.
3. Add a new repository secret named **`GCP_PROJECT_ID`** containing your Google Cloud Project ID.

---

## 🔒 Security & Secrets Management
- The application retrieves database project mappings dynamically via environment variables (`GOOGLE_PROJECT_ID`).
- Do not commit hardcoded API keys or Service Account JSON files to the repository.
- Use Google Cloud **Secret Manager** or **IAM Role Bindings** (such as assigning the `BigQuery Data Viewer` role to your Cloud Run Service Account principal) for authentication in production.

---

## ⚖️ Disclaimer
This is an OSINT research and audit visualization tool. Users are solely responsible for ensuring compliance with local laws, terms of service, and public data access regulations.
