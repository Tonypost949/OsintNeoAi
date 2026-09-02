# Copilot IDE Plugins & Skills Reference

**Last Updated**: 2026-09-01  
**Status**: ✅ All core services connected and verified

---

## 🚀 Quick Access to All Skills

### OSINT & Investigation
| Skill | Purpose | Status |
|-------|---------|--------|
| **osint-forensic-pipeline** | Full-cycle OSINT forensic evidence pipeline (OCR, entity extraction, court-ready dossiers) | ✅ Ready |
| **osint** | OSINT Cabal Live Center (30+ integrated tools, social graph, breach monitoring) | ✅ Ready |

### Life Sciences & Genomics
| Skill | Purpose | Status |
|-------|---------|--------|
| **alphagenome-single-variant-analysis** | Genetic variant effects (RNA-seq, epigenomics, disease associations) | ✅ Ready |
| **clinvar-database** | Clinical variant significance & pathogenicity classifications | ✅ Ready |
| **gnomad-database** | Allele frequency, gene constraints (pLI, LOEUF), structural variants | ✅ Ready |
| **ensembl-database** | Gene/transcript/protein IDs, sequences, genomic structures, VEP | ✅ Ready |
| **uniprot-database** | Protein sequences, domains, Post-translational modifications | ✅ Ready |
| **alphagenome-single-variant-analysis** | AlphaGenome variant effect prediction | ✅ Ready |
| **chembl-database** | Bioactive compounds, drug targets, IC50/Ki values | ✅ Ready |

### Literature & Research
| Skill | Purpose | Status |
|-------|---------|--------|
| **pubmed-database** | PubMed literature search & retrieval | ✅ Ready |
| **literature-search-arxiv** | arXiv preprint search | ✅ Ready |
| **literature-search-biorxiv** | bioRxiv/medRxiv preprint search | ✅ Ready |
| **literature-search-openalex** | OpenAlex scholarly database (DOI, citations, h-index) | ✅ Ready |

### Cloud & Infrastructure
| Skill | Purpose | Status |
|-------|---------|--------|
| **bigquery-sql** | BigQuery SQL queries & data analysis | ✅ Ready |
| **bigquery-graph** | BigQuery Graph analysis (entity relationships) | ✅ Ready |
| **firebase-firestore** | Cloud Firestore database operations | ✅ Ready |
| **firebase-auth-basics** | Firebase Authentication setup | ✅ Ready |
| **firebase-ai-logic-basics** | Firebase AI Logic (Gemini API integration) | ✅ Ready |

### Regulatory & Clinical
| Skill | Purpose | Status |
|-------|---------|--------|
| **openfda-database** | FDA adverse events, recalls, drug approvals | ✅ Ready |
| **clinical-trials-database** | ClinicalTrials.gov search & trial details | ✅ Ready |

---

## 🔌 Connected Plugins & MCP Servers

### Active Plugins
| Plugin | Service | Endpoint | Status |
|--------|---------|----------|--------|
| **Azure DevOps MCP** | Azure DevOps API | `https://mcp.dev.azure.com/anthonydimarcello` | ✅ Running (PID 18900) |
| **GitHub MCP** | GitHub API | `github.com` | ✅ Available |
| **Spark Skills** | Apache Spark | Local/Cloud | ✅ Installed |

### Cloud Services Connected
| Service | Type | Status |
|---------|------|--------|
| **Azure Functions** | Auto-Correlation Engine (ACE) | ✅ Deployed |
| **Azure App Service** | OSINT Web API (osintneoai-app-949) | ✅ 200 OK |
| **Google BigQuery** | Forensic data warehouse | ✅ Connected |
| **Google Drive / OneDrive** | Evidence ingestion | ✅ Configured |
| **Caltrans ArcGIS** | Real-time CCTV cameras (288) | ✅ Live |

---

## ⚙️ Skill Usage Patterns

### OSINT Investigation (Recommended Workflow)
```bash
# 1. Use osint-forensic-pipeline skill for complete end-to-end investigations
   → Evidence ingestion → OCR → Entity extraction → Correlation → Dossier generation

# 2. Use osint skill for quick reconnaissance
   → WHOIS, DNS, IP enumeration, breach database lookups

# 3. Reference literature-search-* skills for background intelligence
```

### Genomic Analysis (Recommended Workflow)
```bash
# 1. Start with clinvar-database for pathogenic variants
# 2. Cross-reference with gnomad-database for population frequencies
# 3. Use alphagenome for functional predictions
# 4. Query PubMed via pubmed-database for literature evidence
# 5. Resolve IDs with ensembl-database for sequence/structure data
```

### BigQuery Analytics (Recommended Workflow)
```bash
# 1. Use bigquery-sql skill to write analytical queries
# 2. Use bigquery-graph skill to find entity relationships
# 3. Load correlation results into visualization dashboard
```

---

## ⚠️ Known Issues & Workarounds

### Issue: Hugging Face Plugin Not Loaded
**Status**: ⚠️ Not critical  
**Workaround**: 
- Use `pubmed-database` + `literature-search-arxiv` for research summaries
- Use `firebase-ai-logic-basics` for Gemini multimodal inference
- OSINT pipeline includes built-in NLP entity extraction

### Issue: PowerApps Connectors
**Status**: ✅ Fixed in app service  
**Details**:
- Custom connector endpoint: `https://osintneoai-app-949.azurewebsites.net`
- Endpoints: `/api/search`, `/api/correlate`, `/api/dossiers`, `/api/submit-victim`
- Power Automate flow: Auto-triggers every 4 hours via `public_notice_keyword_watcher.json`

### Issue: Rate Limiting on Public APIs
**Status**: ⚠️ May occur under load  
**Workaround**:
- Use BigQuery + ClinVar mirror for genomic queries (no rate limits)
- Use PubMed E-utilities with API key (higher quota)
- Use local cache for Caltrans CCTV data (updated every 5 min via ACE)

---

## 🎯 Integration Points in OsintNeoAi

### ACE (Auto-Correlation Engine)
**Skills Used**:
- `osint-forensic-pipeline` → Entity extraction & correlation
- `bigquery-sql` → Load correlation results to warehouse
- `bigquery-graph` → Generate correlation network

### God's Eye View (3D Tactical Globe)
**Skills Used**:
- `osint` → Investigation node coordinates
- `caltrans_d12_pull.py` → 288 live CCTV cameras (GeoJSON)
- `bigquery-graph` → Render correlation clusters as geo-markers

### Whistleblower Briefing Generator
**Skills Used**:
- `literature-search-openalex` → Case law & precedent search
- `pubmed-database` → Medical evidence for injury claims
- `clinvar-database` → Genetic/health fact-checking

---

## 🔧 How to Test Connectivity

```bash
# Test Azure DevOps MCP
gh api graphql -f query='{ viewer { login } }'

# Test BigQuery
bq ls --project=noble-beanbag-497411-m4

# Test Firebase
gcloud auth login && gcloud app describe

# Test OSINT Forensic Pipeline
python auto_correlation_enrichment_engine.py --test

# Test Caltrans API
curl "https://caltrans-gis.dot.ca.gov/arcgis/rest/services/CHhighway/CCTV/FeatureServer/0/query?where=district%3D%2712%27&returnGeometry=true&f=json&resultRecordCount=5"
```

---

## 📞 Support & Troubleshooting

**All plugins reloaded successfully on 2026-09-01 at 12:34 UTC**

If a skill isn't working:
1. Check `/logs/extensions/*.log` for error messages
2. Verify API credentials (GitHub token, GCP service account, etc.)
3. Run `extensions_reload` to reinitialize
4. Use `extensions_manage inspect <skill-name>` to debug

For PowerApps connectors, verify endpoints via:
```bash
curl -I https://osintneoai-app-949.azurewebsites.net/api/search
curl -I https://osintneoai-app-949.azurewebsites.net/api/correlate
```

---

**For full API reference, see**:
- **OSINT**: `docs/OSINT_INTEGRATION_GUIDE.md`
- **ACE**: `docs/ACE_DEPLOYMENT_GUIDE.md`
- **Forensics**: `docs/MASTER_WHISTLEBLOWER_EVIDENCE_BRIEFING_2026.md`
