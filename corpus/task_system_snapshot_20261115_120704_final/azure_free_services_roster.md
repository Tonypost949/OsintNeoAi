# Azure Free Services Provisioning & Registration Roster
**Source URL:** `https://portal.azure.com/#view/Microsoft_Azure_Billing/FreeServicesBlade`  
**Subscription ID:** `c7c9b67b-33c7-4201-ada2-ae6c0c42fe7e` (Azure subscription 1)  
**Tenant ID:** `35498253-edeb-4502-b104-4a7748358b5b` (`anthony.dimarcello.student@gmail.com`)  
**Resource Group Target:** `rg-free-tier-services-westus`  
**Execution Timestamp:** 2026-10-26T18:42:00-07:00  

---

## 1. Always Free Tier Services (Activated / Registered)

| # | Service Name | SKU / Tier | Free Monthly Allocation | Deployment Command / Config |
|---|---|---|---|---|
| 1 | **Azure App Service** | F1 (Free) | 10 Apps, 1 GB storage, 60 CPU min/day | `az appservice plan create --name plan-free-f1 --sku F1` |
| 2 | **Azure Functions** | Dynamic (Consumption) | 1,000,000 executions/month | Built into serverless consumption |
| 3 | **Azure Cosmos DB** | Free Tier (1,000 RU/s + 25 GB) | 1,000 RU/s throughput + 25 GB storage 100% free lifetime | `az cosmosdb create --enable-free-tier true` |
| 4 | **Azure AI Search (Cognitive Search)** | Free (F) | 50 MB storage, 3 indexes, 10,000 docs | `az search service create --sku free` |
| 5 | **Azure AI Services (Multi-service)** | F0 (Free) | 5,000 text records, 20 pages Document AI, 5 hrs Speech | `az cognitiveservices account create --sku F0` |
| 6 | **Azure Event Grid** | Free | 100,000 operations/month | Serverless event routing |
| 7 | **Azure Key Vault** | Standard (Free allowance) | 10,000 secret/key transactions/mo | `az keyvault create` |
| 8 | **Azure DevOps** | Free Basic (5 users) | Unlimited private repos, 1,800 build mins/month | `https://dev.azure.com/anthonydimarcello` |
| 9 | **Azure Notification Hubs** | Free (F0) | 1,000,000 push notifications/mo | Push broadcast alerts |
| 10 | **Azure Service Bus** | Basic (Shared Free tiers) | 750,000 operations/mo | Enterprise message queuing |

---

## 2. 12-Month Free Services (First Year Allocation)

| # | Service Name | SKU / Tier | Free Allocation |
|---|---|---|---|
| 11 | **Linux Virtual Machine** | B1s (1 vCPU, 1 GB RAM) | 750 hours/month (Runs 24/7 for 1 year free) |
| 12 | **Windows Virtual Machine** | B1s (1 vCPU, 1 GB RAM) | 750 hours/month (Runs 24/7 for 1 year free) |
| 13 | **Standard SSD Storage** | E6 (Managed Disk) | 2x 64 GB disks + 1 GB snapshot storage |
| 14 | **Azure Blob Storage** | LRS Hot / Cool | 5 GB LRS storage + 20,000 read/10,000 write ops |
| 15 | **Azure SQL Database** | S0 (10 DTUs, 250 GB storage) | 1 database (12 months free) |
| 16 | **Bandwidth / Egress** | Data Transfer Out | 15 GB outbound internet data per month |

---

## 3. Autonomous Execution Script
* **Deployment Script:** `C:\Amd949609_Antigravity_v1\tools\task_system\provision_azure_free_services.ps1`
* **Automated Log:** `C:\Amd949609_Antigravity_v1\tools\task_system\completed_ledger.md`
