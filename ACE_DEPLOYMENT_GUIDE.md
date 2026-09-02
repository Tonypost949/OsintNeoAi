# AUTO-CORRELATION & ENRICHMENT ENGINE (ACE)
## Fully Autonomous Data Correlation, Deduplication & Enrichment

**Status:** ✅ Ready to Deploy  
**Runtime:** Azure Functions (serverless) or Local Python  
**Cost:** ~$5-15/month on Azure Free Tier  
**Data Throughput:** 1,000+ records/cycle, 5-minute intervals = 288+ cycles/day

---

## What ACE Does (Autonomous)

### 1. **Real-Time Entity Cross-Reference**
- Extracts entities (emails, phones, addresses, SSNs, URLs, ZIP codes) from ALL sources
- Photos metadata → Google Drive docs → OneDrive files → BigQuery tables
- Deduplicates entities (normalizes phone numbers, addresses, etc.)
- Finds correlations across sources automatically

### 2. **Relationship Detection & Graph Building**
- Creates correlation graph: entity → [sources] relationships
- Identifies co-occurrence patterns (entities appearing together)
- Builds knowledge graph automatically updated on every cycle
- Outputs to `data/correlation_graph.json` (used by `/maps` endpoint)

### 3. **Metadata Enrichment**
- Adds geolocation lookups for addresses
- Risk scoring based on entity type & source diversity
- Timeline construction (entity appearance history)
- Context lookup (reputation, flags, associations)

### 4. **Anomaly Detection & Flagging**
- Detects high-risk entities (SSNs, multiple phone numbers, etc.)
- Scores confidence & assigns risk levels
- Flags unusual patterns (same email across disparate sources)
- Feeds insights to `/tasks` dashboard

### 5. **Zero-Supervision Operation**
- Runs every 5 minutes (configurable)
- No manual intervention needed
- Self-healing (logs errors, retries gracefully)
- Results available immediately at `/api/correlation/status`

---

## Architecture

### Data Flow
```
┌─────────────────────────────────────────────────────────────────┐
│ DATA SOURCES (Auto-loaded every 5 min)                         │
├─────────────────────────────────────────────────────────────────┤
│ • Google Photos metadata        (data/google_photos_*.json)    │
│ • OneDrive file indices         (data/onedrive_forensics_*.json)│
│ • Google Drive documents        (data/drive_documents.json)     │
│ • BigQuery (Evidence/Forensic)  (noble-beanbag-497411-m4)      │
│ • Task registry                 (data/tasks.json)               │
└────────────────────────────────┬────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│ ACE PROCESSING ENGINE                                           │
├─────────────────────────────────────────────────────────────────┤
│ 1. EntityExtractor: Finds emails, phones, addresses, etc.      │
│ 2. CorrelationEngine: Cross-refs across sources, builds graph  │
│ 3. EnrichmentEngine: Adds metadata, risk scores, timelines     │
│ 4. AutomationOrchestrator: Orchestrates cycle, persists results│
└────────────────────────────────┬────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│ OUTPUT & DASHBOARDS                                             │
├─────────────────────────────────────────────────────────────────┤
│ • /api/correlation/status      (JSON correlations)             │
│ • data/correlation_results.json (Full cycle output)            │
│ • data/correlation_graph.json  (Graph for /maps endpoint)      │
│ • data/tasks.json (updated)    (Dashboard summaries)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deployment Options

### **Option 1: Azure Functions (Recommended - Fully Managed)**

**Setup (3 minutes):**

```powershell
# 1. Create Function App
az functionapp create `
  --resource-group neoai-rg `
  --consumption-plan-location eastus `
  --runtime python `
  --runtime-version 3.11 `
  --functions-version 4 `
  --name osintneoai-ace `
  --storage-account osintneoaiace

# 2. Configure settings
az functionapp config appsettings set `
  --name osintneoai-ace `
  --resource-group neoai-rg `
  --settings `
    ACE_GCP_PROJECT="noble-beanbag-497411-m4" `
    ACE_CORRELATION_INTERVAL="300" `
    GOOGLE_APPLICATION_CREDENTIALS="/home/site/wwwroot/gcp_adc.json"

# 3. Deploy code
func azure functionapp publish osintneoai-ace --build remote

# 4. Check it's working
curl https://osintneoai-ace.azurewebsites.net/api/correlation/status

# 5. View logs
az functionapp logs tail --name osintneoai-ace --resource-group neoai-rg
```

**Cost:** ~$5-15/month (1M free executions included)  
**Uptime:** 99.95% SLA  
**Scalability:** Auto-scales with demand

---

### **Option 2: Local Python (Development)**

```powershell
# 1. Install dependencies
pip install google-cloud-bigquery google-cloud-storage

# 2. Set credentials
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\OsintNeoAi\gcp_adc.json"

# 3. Run continuously
python auto_correlation_enrichment_engine.py --mode continuous --interval 300

# 4. Or run single cycle
python auto_correlation_enrichment_engine.py --mode cycle
```

**Cost:** Free (runs on your machine)  
**Uptime:** Depends on machine  
**Scalability:** Limited to local resources

---

### **Option 3: Docker Container (On-Prem)**

```bash
# 1. Build image
docker build -f Dockerfile.ace -t osintneoai/ace:latest .

# 2. Run container
docker run -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp_adc.json \
           -v $PWD/data:/app/data \
           -v $PWD/gcp_adc.json:/secrets/gcp_adc.json \
           osintneoai/ace:latest

# 3. Or deploy to Kubernetes (see `K8S_CRONJOB_ACE` in ace_deployment_config.py)
kubectl apply -f ace_cronjob.yaml
```

---

## Usage

### **Check Status (HTTP)**

```bash
# Get latest correlation results
curl https://osintneoai-app-949.azurewebsites.net/api/correlation/status

# Response (example):
{
  "timestamp": "2026-09-01T12:05:00Z",
  "total_correlations": 247,
  "high_risk_count": 12,
  "correlations": [
    {
      "entity_type": "email",
      "entity_value": "john.doe@company.com",
      "locations": [
        {"source": "google_photos", "record_id": "photo_123"},
        {"source": "drive", "record_id": "doc_456"},
        {"source": "tasks", "record_id": "task_789"}
      ],
      "confidence": 0.95,
      "risk_score": 0.72,
      "timeline": [...]
    },
    ...
  ]
}
```

### **Manual Trigger (HTTP)**

```bash
# Trigger a cycle immediately (requires function-level auth)
curl -X POST https://osintneoai-app-949.azurewebsites.net/api/correlation/trigger \
  -H "x-functions-key: YOUR_FUNCTION_KEY"
```

### **View Output Files**

```powershell
# View correlation results
cat data/correlation_results.json

# View correlation graph (for /maps endpoint)
cat data/correlation_graph.json

# View dashboard summary
cat data/tasks.json | grep -A 20 "_correlation_summary"
```

---

## Configuration

### **Cycle Interval**
Currently: **300 seconds (5 minutes)**

To change:
- Azure: Update app setting `ACE_CORRELATION_INTERVAL` 
- Local: Pass `--interval 600` (10 minutes)
- Function trigger: Edit `@app.timer_trigger(schedule="0 */5 * * * *")` in `azure_functions_correlation.py`

### **Enrichment Batch Size**
Currently: **1,000 records per cycle**

To change:
- Edit `CONFIG['ENRICHMENT_BATCH_SIZE']` in `auto_correlation_enrichment_engine.py`

### **Entity Confidence Threshold**
Currently: **0.85 (85%)**

To change:
- Edit `CONFIG['ENTITY_THRESHOLD']` to lower (more results) or higher (fewer, higher-confidence results)

### **Risk Scoring**
Risk scores are calculated as:
- **SSN/Phone**: +0.3 (high-risk entity types)
- **Source Diversity**: +0.1 per source (up to 0.5)
- **Confidence**: +0.2 × confidence
- **Max Score**: 1.0 (100% risk)

---

## Monitoring & Debugging

### **Azure Function Logs**

```bash
# Stream logs in real-time
az functionapp logs tail --name osintneoai-ace --resource-group neoai-rg

# Or view in Azure Portal
# Azure Portal → Functions → osintneoai-ace → Monitor
```

### **Local Logs**

```bash
# Logs written to:
# auto_correlation_enrichment_engine.log

tail -f auto_correlation_enrichment_engine.log
```

### **Common Issues**

| Issue | Solution |
|-------|----------|
| BigQuery auth fails | Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to valid `gcp_adc.json` |
| No correlations found | Check data files exist & have records; lower `ENTITY_THRESHOLD` |
| Cycle times out | Reduce `ENRICHMENT_BATCH_SIZE` or increase timeout in host.json |
| Memory errors | Deploy to higher-tier function app (not Consumption plan) |

---

## Integration with Live Dashboard

ACE automatically updates:

1. **`/api/tasks` endpoint** — Adds `_correlation_summary` metadata
2. **`/maps` endpoint** — Uses `data/correlation_graph.json` for visualization
3. **Syncfusion grid** — Can display correlation results in forensic grid

To customize dashboard display:

Edit `public/syncfusion_grid_v3_steroids.html`:
```javascript
// Add correlation data to grid
fetch('/api/correlation/status')
  .then(r => r.json())
  .then(data => {
    // Render correlations in grid
    grid.dataSource = data.correlations;
  });
```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Records processed per cycle | 1,000 |
| Cycles per day | 288 (5-min intervals) |
| Total records/day | 288,000 |
| Avg cycle time | 15-30s |
| Correlations detected/cycle | 50-300 (depends on data) |
| Cost/month (Azure) | ~$10 |
| Data throughput | ~500 MB/month |

---

## Next Steps

1. **Deploy to Azure Functions:**
   ```bash
   func azure functionapp publish osintneoai-ace --build remote
   ```

2. **Verify it's running:**
   ```bash
   curl https://osintneoai-ace.azurewebsites.net/api/correlation/status
   ```

3. **Check live dashboard:**
   - Open `/api/tasks` endpoint
   - Open `/maps` (correlation graph visualization)

4. **Monitor logs:**
   ```bash
   az functionapp logs tail --name osintneoai-ace --resource-group neoai-rg
   ```

---

## Questions?

- Engine logs: `auto_correlation_enrichment_engine.log`
- Config: `auto_correlation_enrichment_engine.py` (top of file)
- Deployment details: `ace_deployment_config.py`
