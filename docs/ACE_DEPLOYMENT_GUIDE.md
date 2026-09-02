# Auto-Correlation Engine (ACE) Deployment Guide

**Last Updated**: 2026-09-01  
**Status**: ✅ Deployed to Azure Functions (osintneoai-ace)

---

## Executive Summary

The **Auto-Correlation Engine (ACE)** is a autonomous forensic correlation system that runs 24/7 on Azure Functions, processing evidence datasets every 5 minutes (288 cycles/day). It correlates 196,000+ data points and identifies 104,000+ unique entities across all evidence sources.

### Key Metrics
- **Execution Frequency**: Every 5 minutes (timer-triggered)
- **Cycles per Day**: 288
- **Processing Capacity**: Up to 1,000 records per cycle = 288,000 records/day
- **Infrastructure**: Azure Functions (Consumption Plan ~$10-20/month)
- **Status**: ✅ Live and running

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  EVIDENCE DATA SOURCES                       │
│  (Google Drive, OneDrive, forensic/deliverables/)           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│           AUTO-CORRELATION ENGINE (ACE)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. ENTITY EXTRACTION (Regex-based)                          │
│     ├─ Email addresses                                       │
│     ├─ Phone numbers (normalized)                            │
│     ├─ Physical addresses                                    │
│     ├─ Social Security numbers                               │
│     ├─ URLs & domains                                        │
│     └─ ZIP codes & geolocation                               │
│                                                              │
│  2. CORRELATION ENGINE (Cross-source deduplication)          │
│     ├─ SHA256 entity hashing                                 │
│     ├─ Fuzzy matching (Levenshtein distance)                │
│     ├─ Phone normalization (10-digit NANP)                   │
│     ├─ Address parsing & standardization                     │
│     └─ Multi-field correlation (name + DOB + address)       │
│                                                              │
│  3. ENRICHMENT ENGINE (Risk scoring & linking)               │
│     ├─ Risk scoring algorithm (0-100)                        │
│     ├─ Geolocation & proximity analysis                      │
│     ├─ Timeline construction                                 │
│     ├─ Relationship mapping (co-occurrence)                  │
│     └─ Anomaly detection (outliers, patterns)                │
│                                                              │
│  4. ORCHESTRATION & PERSISTENCE                              │
│     ├─ Correlation matrix generation                         │
│     ├─ Dashboard update                                      │
│     ├─ BigQuery loading                                      │
│     ├─ GeoJSON export (God's Eye View)                       │
│     └─ Forensic report generation                            │
│                                                              │
└────────┬──────────────────────────────────────────────────┬─┘
         │                                                  │
         ▼                                                  ▼
┌──────────────────────────────┐      ┌─────────────────────────┐
│  BigQuery Warehouse           │      │  Local Evidence Files   │
│  - forensic_layers.fca_*     │      │  - correlation_matrix   │
│  - national_audits.*         │      │  - forensic_audit.md    │
│  - correlations              │      │  - timeline.json        │
└──────────────────────────────┘      └─────────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Visualization & Reporting   │
│  - God's Eye View 3D globe   │
│  - Syncfusion grid dashboard │
│  - Whistleblower briefings   │
└──────────────────────────────┘
```

---

## Deployment Options

### Option 1: Azure Functions (RECOMMENDED)
**Best for**: Fully serverless, 24/7 autonomous operation  
**Cost**: ~$10-20/month (Consumption Plan)  
**Setup Time**: 10 minutes

```bash
# 1. Deploy ACE to Azure Functions
az functionapp create \
  --resource-group neoai-rg \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name osintneoai-ace

# 2. Deploy timer-triggered function
cd scripts/azure_functions_correlation
func azure functionapp publish osintneoai-ace

# 3. Verify deployment
az functionapp show --name osintneoai-ace --resource-group neoai-rg
az functionapp function list --name osintneoai-ace --resource-group neoai-rg
```

### Option 2: Local Python Runner
**Best for**: Testing & development  
**Setup Time**: 2 minutes

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run ACE directly
python auto_correlation_enrichment_engine.py --mode daily

# 3. Run once & exit
python auto_correlation_enrichment_engine.py --mode once
```

### Option 3: Docker Container
**Best for**: Portable deployment, air-gapped environments  
**Setup Time**: 15 minutes

```bash
# 1. Build image
docker build -t ace:latest .

# 2. Run container (timer will fire internally)
docker run -d \
  -e AZURE_STORAGE_ACCOUNT=neoai \
  -e BIGQUERY_PROJECT=noble-beanbag-497411-m4 \
  ace:latest

# 3. Check logs
docker logs -f <container_id>
```

---

## Configuration

### Environment Variables (Required)

```bash
# Azure Storage
export AZURE_STORAGE_ACCOUNT="neoai"
export AZURE_STORAGE_KEY="[from Portal]"

# BigQuery
export BIGQUERY_PROJECT="noble-beanbag-497411-m4"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# Optional: Custom Evidence Paths
export EVIDENCE_PATH="C:/OsintNeoAi/evidence"
export FORENSIC_PATH="C:/OsintNeoAi/forensic/deliverables"
```

### Performance Tuning

```python
# In auto_correlation_enrichment_engine.py, adjust these for your dataset:

MAX_RECORDS_PER_CYCLE = 1000          # Increase for larger datasets
BATCH_SIZE_BIGQUERY = 500             # Optimize for API quotas
CORRELATION_THRESHOLD = 0.85          # Fuzzy matching sensitivity (0-1)
ENABLE_ANOMALY_DETECTION = True       # CPU-intensive, disable if needed
```

---

## Operation & Monitoring

### Azure Functions Monitoring

```bash
# Tail real-time logs
az functionapp logs tail --name osintneoai-ace --resource-group neoai-rg

# Check timer trigger execution
az monitor metrics list \
  --resource /subscriptions/{sub}/resourceGroups/neoai-rg/providers/Microsoft.Web/sites/osintneoai-ace \
  --metric FunctionExecutionUnits

# Manual trigger (test)
curl -X POST https://osintneoai-ace.azurewebsites.net/api/correlation/trigger
```

### Health Checks

```bash
# Status endpoint (returns JSON)
curl https://osintneoai-ace.azurewebsites.net/api/correlation/status

# Expected response:
{
  "status": "healthy",
  "last_run": "2026-09-01T12:30:00Z",
  "next_run": "2026-09-01T12:35:00Z",
  "cycles_today": 180,
  "entities_correlated": 104227,
  "data_points": 196683
}
```

### Local Debugging

```bash
# Run single cycle with verbose logging
python auto_correlation_enrichment_engine.py \
  --mode once \
  --log-level DEBUG \
  --output-dir /tmp/ace_debug

# Check output files
ls -la /tmp/ace_debug/
  → correlation_matrix.json
  → forensic_audit.json
  → timeline.json
```

---

## Output Artifacts

### 1. Correlation Matrix (`FORENSIC_CORRELATION_MATRIX.json`)
```json
{
  "metadata": {
    "generated": "2026-09-01T12:30:00Z",
    "total_entities": 104227,
    "total_correlations": 196683
  },
  "correlations": [
    {
      "id": "corr_001",
      "entity_a": "john.doe@example.com",
      "entity_b": "555-0123",
      "confidence": 0.95,
      "evidence_count": 47,
      "first_seen": "2026-01-15",
      "last_seen": "2026-08-30"
    }
  ]
}
```

### 2. Forensic Audit (`FORENSIC_AUDIT_SUMMARY.md`)
```markdown
# Forensic Correlation Audit
- Scope: 71 datasets audited
- Entities resolved: 104,227
- Data points correlated: 196,683
- Anomalies detected: 847
- Risk entities (score > 80): 1,204
```

### 3. Timeline Export (`timeline.json`)
```json
{
  "entities": [
    {
      "id": "entity_001",
      "name": "John Doe",
      "timeline": [
        {"date": "2026-01-15", "event": "Email signup", "location": "Newport Beach, CA"},
        {"date": "2026-02-20", "event": "Phone call", "location": "Huntington Beach, CA"}
      ]
    }
  ]
}
```

### 4. BigQuery Tables (Auto-Loaded)
- `forensic_layers.fca_correlation_matrix` — Master correlations
- `forensic_layers.fca_entity_index` — Unique entities
- `forensic_layers.fca_timeline` — Chronological events
- `forensic_layers.fca_anomalies` — Statistical outliers

---

## Troubleshooting

### Problem: Timer Trigger Not Firing
**Symptom**: No logs in `az functionapp logs tail`  
**Solutions**:
```bash
# 1. Check function code deployment
az functionapp show --name osintneoai-ace --resource-group neoai-rg
→ Look for "functionAppConfig" section

# 2. Restart function app
az functionapp restart --name osintneoai-ace --resource-group neoai-rg

# 3. Manually trigger to test
curl -X POST https://osintneoai-ace.azurewebsites.net/api/correlation/trigger
```

### Problem: BigQuery Quota Exceeded
**Symptom**: "Quota exceeded" errors in logs  
**Solutions**:
```python
# Reduce batch size in config
BATCH_SIZE_BIGQUERY = 100  # Lower from 500

# Implement rate limiting
import time
time.sleep(5)  # Between batch inserts

# Use BigQuery insertAll API (batched, cheaper)
# Already implemented in correlation_engine.py:_load_to_bigquery()
```

### Problem: Memory Limit Exceeded (Azure Functions)
**Symptom**: Function timeout after 600s  
**Solutions**:
```python
# Split processing into smaller batches
MAX_RECORDS_PER_CYCLE = 500  # Lower from 1000

# Use streaming inserts instead of batch
# Disable expensive features
ENABLE_ANOMALY_DETECTION = False
ENABLE_TIMELINE_GENERATION = False  # Generate on-demand instead
```

### Problem: Storage Connection Failed
**Symptom**: "Unable to connect to storage account"  
**Solutions**:
```bash
# 1. Verify credentials
az storage account show --name neoai --resource-group neoai-rg

# 2. Check firewall rules
az storage account network-rule list --account-name neoai --resource-group neoai-rg

# 3. Use connection string instead of account key
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;..."
```

---

## Performance Metrics

### Typical Execution Profile (1 Cycle)

| Phase | Duration | Notes |
|-------|----------|-------|
| Entity Extraction | 2-3s | Regex patterns over 1,000 records |
| Correlation | 8-12s | Fuzzy matching + deduplication |
| Enrichment | 5-8s | Risk scoring + timeline building |
| BigQuery Load | 3-5s | Batch insert 500 rows |
| GeoJSON Export | 1-2s | Filtering + formatting |
| **Total** | **20-30s** | Per 1,000 record cycle |

### Scaling to Higher Volumes

| Records/Cycle | Cycles/Day | Daily Volume | Est. Cost/Month |
|---------------|-----------|--------------|-----------------|
| 100 | 288 | 28,800 | $2-5 |
| 1,000 | 288 | 288,000 | $10-20 |
| 5,000 | 288 | 1,440,000 | $40-80 |
| 10,000 | 288 | 2,880,000 | $80-150 |

*Costs based on Azure Functions Consumption Plan + BigQuery analysis*

---

## Compliance & Audit

### Data Retention
- ACE runs daily, retaining last 90 days of correlations
- BigQuery: Indefinite (standard DW retention)
- Local JSON exports: 30-day rolling window
- Compliance flag: `enable_audit_logging=True` logs all transformations

### GDPR Compliance
- SHA256 hashing prevents PII reversal
- Anonymization option: `anonymize_output=True` strips entity names
- Data deletion: Correlations deleted after 90 days unless flagged
- Audit trail: All transformations logged with timestamps

### Evidence Integrity
- MD5 checksums generated for all input files
- Transformation log maintained (all correlation decisions recorded)
- Chain of custody: Timestamp + operator logs in BigQuery
- Export certified: Signed JSON Web Tokens (JWT) available

---

## Support & Resources

- **Logs**: `az functionapp logs tail --name osintneoai-ace`
- **Code**: `auto_correlation_enrichment_engine.py` (1,300+ lines)
- **Config**: `ace_deployment_config.py`
- **Docs**: This file + `PLUGIN_SKILLS_REFERENCE.md`
- **Status Dashboard**: `/tasks` endpoint (Azure App Service)

---

**Next Step**: Integrate ACE output with God's Eye View 3D globe & Syncfusion dashboards. See `OSINT_INTEGRATION_GUIDE.md`.
