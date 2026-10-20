# OSINT Data Correlation Pipeline, Graph Engine & Interactive Dashboard

## Overview

This project provides an end-to-end open-source OSINT data correlation system, graph database engine, REST query API, and interactive web dashboard. It cross-references public business entity records (Nevada SOS), public SBA PPP loan datasets, municipal property/parcel records, and IRS Form 990 non-profit filings to uncover hidden ownership networks, shared registered agent hubs, and risk clusters.

---

## Directory Layout

```
teamwork_project/
├── pyproject.toml
├── README.md
├── data/
│   └── osint_graph.db         # Persistent SQLite FTS5 graph database
├── src/
│   ├── core/                  # Schemas, USPS normalizers & RapidFuzz matcher
│   ├── engine/                # SQLite store, NetworkX cluster engine & ingestors
│   ├── api/                   # FastAPI backend REST service & routes
│   └── dashboard/             # Streamlit interactive web dashboard UI
└── tests/                     # Pytest suite
```

---

## Quick Start

### 1. Installation

```bash
pip install -e .[dev]
```

### 2. Generate Synthetic OSINT Benchmark Dataset

Generate synthetic mock datasets with shared registered agent address hubs:

```bash
python -m src.engine.mock_generator --output-dir data/mock --num-nodes 1000 --num-hubs 5 --seed 42
```

### 3. Run Ingestion Pipeline

Ingest baseline JSON files or generated CSV datasets into the SQLite graph database:

```bash
python -m src.engine.ingestor --input-dir data/mock --db-path data/osint_graph.db
```

### 4. Run Pytest Suite

```bash
pytest
```

### 5. Launch REST API Server

```bash
uvicorn src.api.app:app --reload --port 8000
```
Swagger API docs will be available at `http://localhost:8000/docs`.

### 6. Launch Web Dashboard

```bash
streamlit run src/dashboard/app.py
```
