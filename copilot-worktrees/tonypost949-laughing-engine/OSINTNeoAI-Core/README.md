# OSINTNeoAI-Core

A unified intelligence mapping platform designed for multi-channel data ingestion, entity resolution, and spatial/graph link-analysis.

## Modular Repository Architecture

```directory
OSINTNeoAI-Core/
├── config/                   # Global configuration & schema validation
├── connectors/               # Ingestion (GDrive, Gmail, OneDrive, OCR)
├── processing/               # Normalization, Aegis correlation & NPI processing
├── graph/                    # Graph database schema mapping, Maltego, & GIS mapping
└── agent/                    # Autonomous loop, AI interactions & CLI controllers
```

### Module Descriptions
1.  **`connectors/`**: Contains API engines to securely ingest records from local storage, cloud environments (OneDrive, Google Drive), mailboxes (Gmail), and un-scannable files (Tesseract/Azure OCR bulk scanner).
2.  **`processing/`**: Powers forensic entity-resolution. Executes corporate record matching (Aegis core correlation engine), workbook normalization, and National Provider Index (NPPES) EIN linkages.
3.  **`graph/`**: Maps high-risk linkages to a schema-enforced network database model. Exports intelligence models directly to Maltego link-charts and GeoJSON spatial maps.
4.  **`agent/`**: Runs the autonomous client loop, orchestrating intelligence harvesting pipelines and driving Gemini API connections.
