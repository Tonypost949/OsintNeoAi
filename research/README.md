# OsintNeoAi Research Papers

Academic papers collected to inform the Spark Intelligence Engine architecture and OSINT methodology.

## Paper Inventory

### Core OSINT Papers (Downloaded)

| ID | Title | Size | Relevance |
|----|-------|------|-----------|
| 2607.03233 | Agentic AI for OSINT Survey | 15.6 MB | Master survey of 74 studies |
| 2608.21471 | OSINT Source Effectiveness | 0.3 MB | Which feeds predict attacks |
| 2603.01245 | AI Whistleblower Office | 1.0 MB | 30 whistleblower cases |
| 2604.09104 | Scheming in the Wild | 1.8 MB | AI incident detection via OSINT |

### Beneficial Ownership / AML Papers (Downloaded)

| ID | Title | Size | Relevance |
|----|-------|------|-----------|
| 2502.19305 | Corporate Fraud Detection GNN | 0.8 MB | Knowledge-enhanced GCN for fraud |
| 2506.04292 | GARG-AML Smurfing | 1.3 MB | Graph-based AML detection |
| 2409.11672 | OSINT Clinic | 1.9 MB | AI-augmented OSINT investigations |

### Municipal Fraud Papers (Downloaded)

| ID | Title | Size | Relevance |
|----|-------|------|-----------|
| 2512.19491 | Sanctioned Government Suppliers | 10.1 MB | PU learning for procurement fraud |
| 2211.01478 | HyperForest Corruption | 3.2 MB | 91% accuracy detecting corrupt contracts |
| 2306.10857 | PANG Pattern Mining | 1.2 MB | Graph patterns for favoritism detection |

### Securities Compliance Papers (Downloaded)

| ID | Title | Size | Relevance |
|----|-------|------|-----------|
| 2604.23585 | ComplianceNLP | 0.4 MB | KG-augmented RAG for regulatory gap detection |
| 2403.00707 | Insider Trading Detection | 1.0 MB | Unsupervised anomaly detection |
| 2605.29427 | FinGuard Compliance | 0.5 MB | LLM compliance detection benchmark |

## Key Findings by Domain

### 1. OSINT & AI Architecture

**Paper:** Agentic AI for OSINT (2607.03233)
- **Core finding:** Hallucination-validation gap — capability outpaces evaluation
- **Key stat:** Only 1 OSINT system empirically measures hallucination (4% RAG rate)
- **Recommendation:** Human-AI co-pilot model; LLMs support collection/triage, analysts retain verification

**Paper:** OSINT Source Effectiveness (2608.21471)
- **Core finding:** 3-source portfolio covers 96.3% of critical infrastructure attacks
- **Key stat:** Fisher exact p = 3.4×10⁻⁸ separation of source profiles
- **Recommendation:** Three operational profiles (precursor, disclosure-exposure, broad-coverage)

### 2. Whistleblower Framework

**Paper:** AI Whistleblower Office (2603.01245)
- **Core finding:** 57-67% of whistleblowers retaliated against; 87%+ morally motivated
- **Key stat:** SEC programme recovered >$4B in penalties
- **Recommendation:** 10-30% financial rewards, anonymous reporting, legal protections

### 3. Beneficial Ownership / AML

**Paper:** Corporate Fraud Detection (2502.19305)
- **Core finding:** Knowledge-enhanced GCN with robust two-stage learning
- **Methodology:** Knowledge graph embeddings for information overload mitigation
- **Application:** Beneficial ownership graph analysis

**Paper:** GARG-AML Smurfing (2506.04292)
- **Core finding:** Second-order neighbourhood analysis for smurfing detection
- **Methodology:** Adjacency matrix density measurements
- **Application:** Shell company detection

**Paper:** OSINT Clinic (2409.11672)
- **Core finding:** AI-augmented collaborative OSINT investigations
- **Methodology:** Co-design with generative AI integration
- **Application:** Spark engine architecture

### 4. Municipal Fraud

**Paper:** Sanctioned Government Suppliers (2512.19491)
- **Core finding:** PU learning detects fraud using sanctions as labels
- **Key stat:** 32% more known positives captured than baseline
- **Methodology:** Network-derived features (eigenvector centrality, core position)

**Paper:** HyperForest Corruption (2211.01478)
- **Core finding:** 91% balanced accuracy detecting corrupt contracts
- **Key stat:** Buyer-supplier relationship features outperform contract features
- **Recommendation:** Corruption is systematic behavior, not isolated anomalies

**Paper:** PANG Pattern Mining (2306.10857)
- **Core finding:** Graph patterns overcome missing tabular data
- **Methodology:** Induced subgraph patterns for favoritism/collusion
- **Application:** Explainable patterns for investigators

### 5. Securities Compliance

**Paper:** ComplianceNLP (2604.23585)
- **Core finding:** Tracks 60,000+ regulatory events/year
- **Key stat:** 12,847 provisions across SEC, MiFID II, Basel III
- **Methodology:** Knowledge-graph-augmented RAG with LEGAL-BERT

**Paper:** Insider Trading Detection (2403.00707)
- **Core finding:** Unsupervised anomaly detection via PCA/autoencoders
- **Methodology:** Reconstruction-based paradigm for trading positions
- **Application:** Market surveillance automation

**Paper:** FinGuard Compliance (2605.29427)
- **Core finding:** Regulation-driven compliance risk taxonomy
- **Key stat:** Expert-annotated benchmark for compliance detection
- **Application:** Automated taxonomy generation from regulatory documents

## Implementation Priority Matrix

| Priority | Paper | Technique | Spark Engine Feature |
|----------|-------|-----------|---------------------|
| P0 | 2607.03233 | Hallucination monitoring | LLM output validation |
| P0 | 2604.23585 | KG-augmented RAG | Regulatory grounding |
| P0 | 2502.19305 | Knowledge graph embeddings | Ownership analysis |
| P1 | 2608.21471 | Source portfolio optimization | Alert prioritization |
| P1 | 2512.19491 | PU learning | Procurement fraud |
| P1 | 2211.01478 | Hyper-Forest ensemble | Imbalanced classification |
| P2 | 2603.01245 | Whistleblower analytics | Compliance framework |
| P2 | 2403.00707 | Autoencoder anomaly detection | Market surveillance |
| P2 | 2306.10857 | Graph pattern mining | Network anomaly detection |

## Methodology Themes

1. **Knowledge Graph Construction** — SEC filing extraction, regulatory KGs
2. **Graph Neural Networks** — Ownership analysis, transaction monitoring
3. **Unsupervised Anomaly Detection** — PCA, autoencoders, reconstruction error
4. **Ensemble + Imbalanced Learning** — SMOTE, XGBoost, random forests
5. **LLM + RAG for Compliance** — Regulation-grounded generation, evidence retrieval
6. **Social Media OSINT** — Telegram/Discord coordination monitoring
7. **RegTech Architecture** — Multi-layer verification, preventive/real-time/investigative

## Not Downloaded (IEEE/Paywall)

| Title | DOI | Notes |
|-------|-----|-------|
| SAKSHI: Agentic AI for Regional Intelligence | 10.1109/icads69450.2026.11545466 | F1=0.84, timelag correlation |
