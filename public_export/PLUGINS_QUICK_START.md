# 🔌 Copilot IDE Plugins & Skills — Quick Start

**Status**: ✅ All plugins verified and connected (2026-09-01 12:34 UTC)

---

## 🚀 Fastest Way to Use Skills

### 1. **OSINT Investigations** (This repo)
```bash
/skill osint-forensic-pipeline
```
Then describe your investigation target. The skill will:
- Ingest evidence from Google Drive/OneDrive
- Extract entities (emails, phones, addresses)
- Generate correlation matrix
- Create court-ready dossier

### 2. **Data Analysis**
```bash
/skill bigquery-sql
```
Query forensic warehouse directly. Example:
```sql
SELECT entity_name, risk_level, correlation_count
FROM forensic_layers.fca_entity_index
WHERE risk_level > 80
ORDER BY correlation_count DESC
```

### 3. **Genomic Research** (If needed)
```bash
@clinvar
```
Look up genetic variants. Will return pathogenicity and clinical evidence.

### 4. **Literature Review**
```bash
@pubmed
```
Search medical/scientific literature. Can fetch full-text PDFs.

---

## 📋 Available Skills by Category

### OSINT & Investigation (Recommended for OsintNeoAi)
| Skill | Usage | Output |
|-------|-------|--------|
| `osint-forensic-pipeline` | Full end-to-end investigations | Court-ready dossier |
| `osint` | Quick reconnaissance | WHOIS, DNS, breach lookup |
| `bigquery-graph` | Entity relationship mapping | Network graph JSON |

### Genomics & Life Sciences
| Skill | Usage | Output |
|-------|-------|--------|
| `clinvar-database` | Pathogenic variants | Clinical significance, evidence |
| `gnomad-database` | Allele frequencies | Population data, constraints |
| `ensembl-database` | Gene/protein sequences | FASTA, structure, annotations |
| `pubmed-database` | Medical literature | Full-text papers, citations |

### Cloud & Infrastructure
| Skill | Usage | Output |
|-------|-------|--------|
| `bigquery-sql` | SQL analytics | Query results, exported data |
| `firebase-firestore` | Real-time database | NoSQL operations |
| `firebase-auth-basics` | User authentication | Auth tokens, SSO |

### Literature & Research
| Skill | Usage | Output |
|-------|-------|--------|
| `literature-search-arxiv` | Research preprints | PDF + metadata |
| `literature-search-biorxiv` | Biology preprints | PDF + metadata |
| `literature-search-openalex` | Scholarly database | DOI resolution, citations |

---

## 🔧 How to Invoke Skills

### Method 1: Slash Command (Easiest)
```
/skill osint
```

### Method 2: @ Mention
```
@pubmed "COVID-19 immunology"
```

### Method 3: In Copilot Workspace
```
/skill bigquery-sql
```
Then paste your SQL query.

---

## ⚙️ Troubleshooting

### Skill Not Responding?
1. **Check if loaded**: `extensions_manage list`
2. **Reload**: `extensions_reload`
3. **Check logs**: `extensions_manage inspect <skill-name>`

### API Credentials Missing?
- Most skills auto-detect credentials from environment
- If needed, store in `.env` or `secrets/` folder
- Use `credentials` skill to manage safely

### Rate Limiting?
- Genomics queries: Use local cache (BigQuery)
- Literature: Use PubMed API key (higher quota)
- OSINT: Batch mode prevents throttling

---

## 📚 Full Documentation

### For OsintNeoAi Developers
- **All 40+ Skills**: [`docs/PLUGIN_SKILLS_REFERENCE.md`](./docs/PLUGIN_SKILLS_REFERENCE.md)
- **ACE Engine**: [`docs/ACE_DEPLOYMENT_GUIDE.md`](./docs/ACE_DEPLOYMENT_GUIDE.md)
- **OSINT Integration**: [`docs/OSINT_INTEGRATION_GUIDE.md`](./docs/OSINT_INTEGRATION_GUIDE.md)

### For Users
- **Quick Access**: Check README.md "QUICK ACCESS" table
- **Live Endpoints**: https://osintneoai-app-949.azurewebsites.net
- **3D Tactical Globe**: https://osintneoai-app-949.azurewebsites.net/gods_eye_view.html

---

## 🎯 Common Tasks

### "Find entities correlated to a location"
```bash
1. /skill osint-forensic-pipeline
2. "Analyze entities near Huntington Beach, CA with high risk score"
3. Output: Correlation matrix + GeoJSON for visualization
```

### "Search for a gene variant"
```bash
1. @clinvar
2. "Look up BRCA1 c.68_69delAG"
3. Output: Pathogenicity, clinical evidence, case reports
```

### "Get allele frequency for a SNP"
```bash
1. @gnomad
2. "Query rs7412 frequency in European populations"
3. Output: AF, AC, AN per population
```

### "Find recent papers on a topic"
```bash
1. @literature-search-openalex
2. "2024 papers on 'machine learning anomaly detection'"
3. Output: 10-50 results with DOI, citations, open access links
```

### "Query forensic database"
```bash
1. /skill bigquery-sql
2. SELECT * FROM forensic_layers.fca_entity_index WHERE risk_level > 80
3. Output: SQL results (CSV downloadable)
```

---

## 🌟 Pro Tips

1. **Combine Skills**: Use OSINT to find targets, then BigQuery to correlate
2. **Batch Operations**: OpenOSINT supports batch mode for 100+ targets
3. **Cache Results**: Caltrans CCTV data auto-refreshes every 5 min (no API call needed)
4. **Export Data**: All outputs are JSON/GeoJSON (import to ArcGIS, QGIS, Power BI)
5. **Audit Trail**: All skill executions logged in `/logs/extensions/*.log`

---

## 📞 Support

**Can't find a skill?**
- Run: `extensions_manage list`
- Check: `docs/PLUGIN_SKILLS_REFERENCE.md` (complete inventory)
- Read: `docs/ACE_DEPLOYMENT_GUIDE.md` (architecture)

**Skill returning errors?**
- Tail logs: `az functionapp logs tail --name osintneoai-ace`
- Test manually: `python auto_correlation_enrichment_engine.py --test`
- Verify credentials in environment variables

**Want to add a new skill?**
- See: `extensions_manage guide` (full authoring guide)
- Example: `extensions_manage scaffold --kind basic --name my-skill`

---

**Last Updated**: 2026-09-01  
**Commit**: c93fce0a (All 40+ skills connected)  
**Status**: ✅ LIVE & OPERATIONAL
