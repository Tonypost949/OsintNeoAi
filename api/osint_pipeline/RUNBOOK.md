# OSINT Pipeline Runbook

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Authenticate GCP
gcloud auth application-default login

# 3. Set BigQuery schema (one-time)
bq query --use_legacy_sql=false < sql/001_schema.sql

# 4. Run Phase 1 (attorney/entity extraction)
python watcher.py

# 5. Run Phase 2 (people/control clusters)
python watcher_v2.py
```

## Architecture

```
watcher.py (Phase 1)
    ├── CA SOS search + detail fetch
    ├── Entity matching (fuzzy + exact, 5-min cache)
    ├── Attorney extraction
    ├── BigQuery MERGE upserts
    └── Neo4j JSONL batch export

watcher_v2.py (Phase 2)
    ├── Load entities from BigQuery
    ├── Person extraction from registered agents
    ├── Person deduplication + merging
    ├── Control cluster detection
    ├── BigQuery upserts
    └── Neo4j JSONL batch export
```

## File Structure

```
osint-pipeline/
├── config.py              # All configuration, env vars
├── entity_match.py        # Fuzzy matching + cache
├── attorney_nodes.py      # Attorney extraction
├── people_handler.py      # Person extraction + clusters
├── neo4j_export.py        # JSONL batch export
├── watcher.py             # Phase 1 main loop
├── watcher_v2.py          # Phase 2 main loop
├── sql/
│   ├── 001_schema.sql     # BigQuery schema
│   └── control_cluster.sql # Cluster detection query
├── tests/
│   └── test_pipeline.py   # Unit tests
├── requirements.txt
└── RUNBOOK.md
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| GCP_PROJECT | project-743aab84-f9a5-4ec7-954 | GCP project ID |
| BQ_DATASET | osint | BigQuery dataset |
| NEO4J_URI | bolt://localhost:7687 | Neo4j connection |
| FUZZY_THRESHOLD | 85 | Minimum match score |
| CACHE_TTL_SECONDS | 300 | Entity cache TTL |
| POLL_INTERVAL_SECONDS | 300 | Watcher poll interval |

## BigQuery Tables

- `entities` — All business entities (CA SOS, PPP, etc.)
- `relationships` — Entity-to-entity links
- `filings` — CA SOS filing documents
- `attorneys` — Registered agent/attorney nodes
- `people` — Deduplicated person nodes
- `control_cluster` — Coordinated entity networks

## Neo4j Import

After running the pipeline, import JSONL batches:

```cypher
// Import entities
LOAD CSV WITH HEADERS FROM 'file:///entities_20260703_123456.jsonl' AS row
CREATE (e:Entity {
    id: row.entity_id,
    name: row.name,
    type: row.type,
    status: row.status
});

// Import relationships
LOAD CSV WITH HEADERS FROM 'file:///rels_20260703_123456.jsonl' AS row
MATCH (a:Entity {id: row.source_id})
MATCH (b:Entity {id: row.target_id})
CREATE (a)-[:RELATED {type: row.type, weight: toFloat(row.weight)}]->(b);
```

## Troubleshooting

**CA SOS 403/Incapsula block:**
- Run from Cloud Workstation (clean IP)
- Or increase delay between requests

**BigQuery auth errors:**
- Run `gcloud auth application-default login`
- Verify project has BigQuery API enabled

**Cache issues:**
- Cache auto-expires after 5 minutes
- Call `clear_cache()` to force refresh
