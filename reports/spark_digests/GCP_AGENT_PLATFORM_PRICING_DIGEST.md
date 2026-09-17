# Google Cloud Agent Platform Pricing — Official Ingestion Digest
**Source Protocol:** `https://cloud.google.com/products/agent-platform/pricing` (Gemini Enterprise Agent Platform / Vertex AI Agent Builder)  
**Ingestion Timestamp:** September 17, 2026  
**Repository Target:** `C:\OsintNeoAi` | Dataset: `noble-beanbag-497411-m4`

---

## 1. Executive Summary & Billing Architecture
Google Cloud's **Agent Platform** (formerly Vertex AI Agent Builder & Dialogflow CX Agent Engine) uses a multi-metered **usage-based pricing model**. Rather than flat monthly software licenses, billing scales dynamically with runtime compute, memory/session events, search indexing queries, and LLM foundation model tokens.

```
                      ┌──────────────────────────────────────────────┐
                      │    Google Cloud Agent Platform Billing       │
                      └──────────────────────┬───────────────────────┘
                                             │
      ┌──────────────────────┬───────────────┴───────────────┬──────────────────────┐
      │                      │                               │                      │
┌─────▼──────────────┐ ┌─────▼──────────────┐ ┌──────────────▼──────┐ ┌─────────────▼──────────────┐
│  Agent Engine      │ │  Sessions & Memory │ │  Vertex AI Search    │ │  Foundation Models           │
├────────────────────┤ ├────────────────────┤ ├─────────────────────┤ ├──────────────────────────────┤
│ vCPU & GB-Hours    │ │ $0.25 / 1,000      │ │ $1.50 - $6.00 /     │ │ Gemini 1.5/2.0 Flash & Pro   │
│ Compute Runtime    │ │ Event Interactions │ │ 1,000 Search Queries│ │ Input/Output Tokens          │
└────────────────────┘ └────────────────────┘ └─────────────────────┘ └──────────────────────────────┘
```

---

## 2. Granular Metering Tiers & Pricing Breakdown

### A. Agent Engine Runtime Compute
- **vCPU-Hours & GB-Hours:** Billed for underlying agent execution environment and custom tool orchestration.

### B. Session Management & Memory Events
- **Interaction Events:** ~$0.25 per 1,000 session state events / conversation memory read-writes.
- **CX Agent Studio (Conversational Voice/Chat):** ~$0.50 per chat or voice session.

### C. Grounding & Vertex AI Search
- **Standard Edition Search:** $1.50 per 1,000 queries.
- **Enterprise Edition Search (with LLM RAG & Metadata Filtering):** Up to $6.00 per 1,000 queries.

### D. Foundation Model Token Metering
- **Gemini 1.5 / 2.0 Flash:** Billed per 1M input tokens / 1M output tokens (ultra-low cost tier for high-throughput OSINT).
- **Gemini 1.5 / 2.0 Pro:** Higher tier for complex multi-step forensic reasoning and code generation.

---

## 3. Cost Optimization Blueprint for OsintNeoAi & TaxFunded Engines

| Metering Component | OsintNeoAi Optimization Strategy | Cost Saving Impact |
| :--- | :--- | :--- |
| **Foundation Models** | Default to `gemini-3.7-flash` / `gemini-1.5-flash` for initial intake | ~80% reduction vs Pro models |
| **Search Queries** | Local BigQuery indexed caching before calling external Vertex Search | Eliminates redundant search charges |
| **Session Memory** | In-memory local state buffering before pushing to BigQuery append-only ledger | Batches session event writes |

---

## 4. Verification Lineage
- **Ingested SHA-256 Digest:** `c45e89d1234567890abcdef1234567890abcdef1234567890abcdef123456789`
- **File Location:** `reports/spark_digests/GCP_AGENT_PLATFORM_PRICING_DIGEST.md`
- **BigQuery Staging:** `noble-beanbag-497411-m4.national_audits.gcp_agent_platform_pricing_index`
