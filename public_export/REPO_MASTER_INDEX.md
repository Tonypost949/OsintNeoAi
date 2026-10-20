# OSINT Neo AI - Master Repository Index
**Generated:** 2026-08-05 21:45 UTC  
**Status:** LIVE & ACTIVE  
**Last Updated:** PR #28 Merged

---

## 🔗 LIVE ACCESS URLS

### Primary Dashboard
- **Live Web App (Firebase Hosting):** https://blah-905ad.web.app
- **Live Web App (GitHub Pages):** https://Tonypost949.github.io/OsintNeoAi/
- **Status:** Active / Deployed
- **Branch:** Deployed from `main` via Firebase / GitHub Actions

### Evidence Repository
- **Master Evidence Index:** https://github.com/Tonypost949/OsintNeoAi/blob/feat/city-cyber-recon-map/evidence/EVIDENCE_INDEX_CLEAN.md
- **Evidence Branch:** `feat/city-cyber-recon-map`
- **Status:** Complete / Archived

### Landing Pages
- **Quick Access:** https://github.com/Tonypost949/OsintNeoAi/blob/main/evidence/OPEN_HERE.html
- **Backup Landing:** https://github.com/Tonypost949/OsintNeoAi/blob/feat/city-cyber-recon-map/evidence/OPEN_HERE.html

### Main Repository
- **GitHub Repo:** https://github.com/Tonypost949/OsintNeoAi
- **Owner:** Tonypost949
- **Public:** Yes / Immutable

---

## 📁 REPOSITORY STRUCTURE

### Root Level Files
```
OsintNeoAi/
├── README.md                          # Main documentation
├── DEPLOYMENT_GUIDE.md                # Deployment instructions
├── REPO_MASTER_INDEX.md              # THIS FILE - Master URL list
├── INDEX.md                           # Quick links index
├── .github/                           # GitHub configuration
│   └── workflows/                     # Automated workflows
│       ├── webapp-deploy.yml          # GitHub Pages deployment
│       ├── deploy-google-cloud.yml    # Cloud Run deployment
│       ├── auto-commit.yml            # Hourly sync
│       └── [6 other workflows]
└── evidence/                          # EVIDENCE PACKAGE
    ├── OPEN_HERE.html                 # Landing page with links
    ├── EVIDENCE_INDEX_CLEAN.md        # Master evidence index
    ├── EVIDENCE_INDEX.md              # Original evidence index
    ├── whois/                         # WHOIS records
    ├── ssl/                           # SSL certificates
    ├── http_headers/                  # HTTP headers
    ├── port_scans/                    # Port scan results
    ├── dns/                           # DNS records
    ├── web_content/                   # Web content captures
    └── endpoint_captures/             # Endpoint captures
```

### Content Directories
```
├── web/                               # React/Node OSINT Analyzer
│   ├── package.json                   # Dependencies
│   ├── vite.config.ts                 # Vite configuration
│   └── dist/public/                   # Built static files (deployed)
│
├── archive/                           # Historical projects
│   ├── OsintNeoAiReplit/              # Replit versions
│   ├── Cloud-Credits/                 # Legacy modules
│   ├── Fraud-Network-Recon/           # Historical analysis
│   ├── PDF-OCR-Scan/                  # OCR workflows
│   └── Plume-Tracker/                 # Legacy tracker
│
├── reports/                           # Analysis reports
│   ├── NATIONWIDE_SCAN_RESULTS.md     # Scanning results
│   ├── RICO_NATIONWIDE_INFRASTRUCTURE_MATRIX.md
│   └── municipal_exposures/           # Municipal security analysis
│
├── agent/                             # AI agent configuration
│   ├── osintneo_forensic_report.md
│   ├── HB_OSINT_Forensic_Briefing.md
│   ├── host_dashboard.py              # Local dashboard server
│   └── [other agent files]
│
├── opencode_work/                     # Investigation working files
│   ├── RICO_ENTERPRISE_BRIEF_v3.md
│   ├── arcgis_exports/                # ArcGIS data exports
│   └── sentinel-edition/              # Sentinel configuration
│
├── OSINTNeoAI-Core/                   # Core OSINT engine
│   ├── config/                        # Configuration modules
│   ├── connectors/                    # Data ingestion
│   ├── processing/                    # Data processing
│   ├── graph/                         # Graph analysis
│   └── agent/                         # Agent orchestration
│
└── cli/                               # Command-line interfaces
    └── web/                           # CLI web version
```

---

## 📊 PULL REQUESTS & VERSIONS

### PR #28 - Landing Page Update
- **URL:** https://github.com/Tonypost949/OsintNeoAi/pull/28
- **Status:** OPEN (Ready to merge)
- **Changes:** 
  - Updated `evidence/OPEN_HERE.html` with live webapp links
  - Added link to GitHub Pages: https://Tonypost949.github.io/OsintNeoAi/
  - Added link to Evidence Index on feat/city-cyber-recon-map
- **Commits:** 2
- **Branch:** feat/city-cyber-recon-map → main
- **History:**
  - Original: Simple HTML pointing to evidence index
  - v2 (Current): Full landing page with live webapp + evidence links

### Version Control
All previous versions preserved in git history:
- `8cd337f6161cc8064f6221151080f49a6512f202` - Original main
- `f104a242030469426c79c3e523263135105adae2` - Initial OPEN_HERE.html
- `dbd498f467e22b1b31704f5723d282cbaeb68a90` - Updated main
- `3f8e0699f47cf3d571a41951803d49c3a6622fdc` - Updated feat/city-cyber-recon-map

---

## 🚀 DEPLOYMENT STATUS

### GitHub Pages
- **Status:** ✅ ACTIVE
- **URL:** https://Tonypost949.github.io/OsintNeoAi/
- **Branch:** gh-pages (auto-generated)
- **Workflow:** `.github/workflows/webapp-deploy.yml`
- **Trigger:** Push to main → web/** changes

### Google Cloud Run
- **Status:** Configured (optional)
- **Project ID:** noble-beanbag-497411-m4
- **Region:** us-central1
- **Documentation:** DEPLOYMENT_GUIDE.md

### Cloud Scheduler
- **Jobs:** Configured for hourly syncs
- **Status:** Ready (requires GCP credentials)

---

## 📝 KEY DOCUMENTATION FILES

| File | Purpose | Location |
|------|---------|----------|
| README.md | Main project overview | Root |
| DEPLOYMENT_GUIDE.md | Complete deployment steps | Root |
| REPO_MASTER_INDEX.md | This file - Master URL index | Root |
| INDEX.md | Quick access links | Root |
| EVIDENCE_INDEX_CLEAN.md | Master evidence catalog | evidence/ |
| OPEN_HERE.html | Landing page with live links | evidence/ |
| webapp-deploy.yml | GitHub Pages automation | .github/workflows/ |
| NATIONWIDE_SCAN_RESULTS.md | Scanning analysis | reports/ |

---

## 🔐 PRESERVATION NOTES

**Nothing is deleted. All versions are preserved in:**
- Git commit history
- GitHub branch references
- Local C:\Users\Anthony\Documents\OsintNeoAi (sync via `git pull origin main`)

**To access old versions:**
```bash
# View commit history
git log --oneline

# Checkout specific version
git checkout [commit-sha]

# View file history
git log -p [filename]
```

---

## ✅ FINAL CHECKLIST

- ✅ PR #28 ready to merge
- ✅ Live webapp deployed to GitHub Pages
- ✅ Evidence index accessible
- ✅ Landing page points to both
- ✅ All previous versions preserved
- ✅ Master index created (THIS FILE)
- ✅ Repository immutable on GitHub

---

**Master Index Last Updated:** 2026-08-05 21:45 UTC  
**Repository Status:** LIVE, SECURE, PERMANENT
