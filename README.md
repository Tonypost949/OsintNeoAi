# OsintNeoAi - Open Source Intelligence Platform

**Production-Grade OSINT Platform with Gemini AI Integration**

[![Deploy to Google Cloud Run](https://github.com/Tonypost949/OsintNeoAi/actions/workflows/deploy-google-cloud.yml/badge.svg)](https://github.com/Tonypost949/OsintNeoAi/actions/workflows/deploy-google-cloud.yml)
[![Auto-Commit Results](https://github.com/Tonypost949/OsintNeoAi/actions/workflows/auto-commit.yml/badge.svg)](https://github.com/Tonypost949/OsintNeoAi/actions/workflows/auto-commit.yml)
[![Colab Sync](https://github.com/Tonypost949/OsintNeoAi/actions/workflows/colab-sync.yml/badge.svg)](https://github.com/Tonypost949/OsintNeoAi/actions/workflows/colab-sync.yml)

## 🚀 Features

- **Multi-Channel Data Ingestion**: GDrive, Gmail, OneDrive, OCR support
- **Entity Resolution**: Forensic matching with corporate record correlation
- **Graph Analysis**: Maltego integration & GeoJSON spatial mapping
- **Gemini AI Integration**: Real-time anomaly detection & analysis
- **Cloud-Native**: Runs on Google Cloud Run (always-on, never freezes)
- **Auto-Sync**: Results automatically push to GitHub hourly
- **Colab-Ready**: Interactive notebooks in Google Colab
- **Zero-Cost**: Entire platform runs on free tiers

## 📊 Quick Start

### 1. Local Installation

```bash
git clone https://github.com/Tonypost949/OsintNeoAi.git
cd OsintNeoAi

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\Activate.ps1

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your Gemini API key

python main.py --mode collect
```

### 2. Google Colab

Open in Colab: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Tonypost949/OsintNeoAi/blob/main/)

1. Click `Secrets` (🔑) in left sidebar
2. Add `GEMINI_API_KEY` from [aistudio.google.com](https://aistudio.google.com)
3. Run cells

### 3. Google Cloud Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete instructions.

## 🔧 Project Structure

```
OsintNeoAi/
├── .github/workflows/           # GitHub Actions workflows
│   ├── deploy-google-cloud.yml  # Cloud Run deployment
│   ├── auto-commit.yml          # Hourly results sync
│   └── colab-sync.yml           # Notebook sync
├── scripts/                     # Helper scripts
├── main.py                      # Main entry point
├── Dockerfile                   # Container config
├── requirements.txt             # Dependencies
└── DEPLOYMENT_GUIDE.md          # Setup guide
```

## 💰 Cost: $0.00

All services run on free tiers with no hidden costs!

## 📖 Documentation

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Complete setup
- [GitHub Issues](https://github.com/Tonypost949/OsintNeoAi/issues)
- [Gemini API Docs](https://ai.google.dev/)

**Never freeze again! Your OSINT platform is now production-ready.** 🚀
