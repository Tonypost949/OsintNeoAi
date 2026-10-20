# Azure Deployment Plan

> **Status:** Planning

Generated: 2026-09-10T01:55:00Z

---

## 1. Project Overview

**Goal:** Deploy the OsintNeoAi Immutable Eviction Wiki & Citizen Intelligence Workspace to Azure. The application consists of a Flask API backend (api/main_v2.py) with Genesis Ingestion Engine, Ledger Hunter, Lockbox Vault, BigQuery integration, and a single-file HTML/JS frontend (workspace_v2.html) served by the same Flask app.

**Path:** Modernize Existing

---

## 2. Requirements

| Attribute | Value |
|-----------|-------|
| Classification | Production |
| Scale | Small (<1K users) |
| Budget | Cost-Optimized |
| **Subscription** | ⚠️ MUST confirm with user |
| **Location** | ⚠️ MUST confirm with user |

---

## 3. Components Detected

| Component | Type | Technology | Path |
|-----------|------|------------|------|
| Flask API Backend | API | Python 3.11, Flask, Gunicorn | api/main_v2.py |
| Frontend Workspace | Frontend | HTML/CSS/JS (single file) | workspace_v2.html |
| BigQuery Integration | Data | google-cloud-bigquery | api/main_v2.py |
| Genesis Ingestion Engine | API | Custom / Gemini LLM | api/main_v2.py:/api/genesis/ingest |
| Ledger Hunter | API | BigQuery + Custom | api/main_v2.py:/api/ledger/* |
| Lockbox Vault | API | File-based + Hash | api/main_v2.py:/api/lockbox/* |
| OSINT Pipeline | Worker | Python | api/osint_pipeline/ |

---

## 4. Recipe Selection

**Selected:** AZD (Azure Developer CLI)

**Rationale:** AZD provides the simplest path for containerized Flask apps with managed infrastructure (Container Apps, Container Registry, Log Analytics, Key Vault). The app already has a Dockerfile and requirements.txt.

---

## 5. Architecture

**Stack:** Containers (Azure Container Apps)

### Service Mapping

| Component | Azure Service | SKU |
|-----------|---------------|-----|
| Flask API + Frontend | Azure Container Apps | Consumption (Cost-Optimized) |
| Container Registry | Azure Container Registry | Basic |
| Log Analytics Workspace | Azure Monitor Log Analytics | Pay-as-you-go |
| Application Insights | Azure Monitor App Insights | Standard |
| Key Vault | Azure Key Vault | Standard |
| Managed Identity | Azure Entra ID | N/A |

### Supporting Services

| Service | Purpose |
|---------|---------|
| Log Analytics | Centralized logging for Container Apps |
| Application Insights | Monitoring & APM for Flask app |
| Key Vault | Secrets management (GEMINI_API_KEY, GOOGLE_CREDENTIALS_JSON) |
| Managed Identity | Service-to-service auth (Container Apps → ACR, Key Vault) |

---

## 6. Provisioning Limit Checklist

### Phase 1: Prepare Resource Inventory

| Resource Type | Number to Deploy | Total After Deployment | Limit/Quota | Notes |
|---------------|------------------|------------------------|-------------|-------|
| Microsoft.App/managedEnvironments | 1 | _TBD_ | _TBD_ | _TBD_ |
| Microsoft.App/containerApps | 1 | _TBD_ | _TBD_ | _TBD_ |
| Microsoft.ContainerRegistry/registries | 1 | _TBD_ | _TBD_ | _TBD_ |
| Microsoft.OperationalInsights/workspaces | 1 | _TBD_ | _TBD_ | _TBD_ |
| Microsoft.Insights/components | 1 | _TBD_ | _TBD_ | _TBD_ |
| Microsoft.KeyVault/vaults | 1 | _TBD_ | _TBD_ | _TBD_ |
| Microsoft.Network/publicIPAddresses | 0 | _TBD_ | _TBD_ | Container Apps uses managed ingress |

### Phase 2: Fetch Quotas and Validate Capacity

**Action:** MUST invoke azure-quotas skill to populate quota data before presenting plan.

---

## 7. Execution Checklist

### Phase 1: Planning
- [x] Analyze workspace
- [ ] Gather requirements
- [ ] Confirm subscription and location with user
- [ ] Prepare resource inventory (Step 6 Phase 1: list resource types and deployment quantities)
- [ ] Fetch quotas and validate capacity (Step 6 Phase 2: invoke azure-quotas skill to use quota CLI)
- [ ] Scan codebase
- [ ] Select recipe
- [ ] Plan architecture
- [ ] **User approved this plan**

### Phase 2: Execution
- [ ] Research components (load references, invoke skills)
- [ ] Generate infrastructure files following service-specific guidance
- [ ] Apply recipes for integrations (if needed)
- [ ] Generate application configuration
- [ ] Generate Dockerfiles (if containerized)
- [ ] **⛔ Update plan status to "Ready for Validation"**

### Phase 3: Validation
- [ ] **PREREQUISITE:** Plan status MUST be "Ready for Validation"
- [ ] Invoke azure-validate skill
- [ ] All validation checks pass
- [ ] Update plan status to "Validated"
- [ ] Record validation proof below

### Phase 4: Deployment
- [ ] Invoke azure-deploy skill
- [ ] Deployment successful
- [ ] Report deployed endpoint URLs
- [ ] Update plan status to "Deployed"

---

## 8. Validation Proof

> **⛔ REQUIRED**: The azure-validate skill MUST populate this section before setting status to `Validated`.

| Check | Command Run | Result | Timestamp |
|-------|-------------|--------|-----------|

**Validated by:** azure-validate skill
**Validation timestamp:** {timestamp}

---

## 9. Files to Generate

| File | Purpose | Status |
|------|---------|--------|
| `.azure/deployment-plan.md` | This plan | ✅ |
| `azure.yaml` | AZD configuration | ⏳ |
| `infra/main.bicep` | Infrastructure | ⏳ |
| `Dockerfile` | Container build (update existing) | ⏳ |
| `requirements.txt` | Python dependencies (update if needed) | ⏳ |

---

## 10. Next Steps

> Current: Phase 1 - Planning

1. Confirm subscription and location with user
2. Check Azure Policy constraints on the subscription
3. Invoke azure-quotas skill to validate capacity
4. Complete plan and present for approval