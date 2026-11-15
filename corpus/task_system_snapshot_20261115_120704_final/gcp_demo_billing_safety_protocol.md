# Google Cloud Demo Safety Architecture (Active Billing with Zero Charges)
**Billing Account:** `01DF70-456C51-E3241B`  
**Rule:** Allow demo APIs requiring active billing to run, while guaranteeing 0 credit card charges.

---

### Step 1: Link ONLY the Demo Project
When a demo specifically requires active billing enabled, link ONLY that project:
```bash
gcloud billing projects link <PROJECT_ID> --billing-account=01DF70-456C51-E3241B
```

### Step 2: Google's Credit Depletion Priority
1. Google Cloud ALWAYS burns promotional/demo credits FIRST before touching any card.
2. In Billing > Credits (`https://console.cloud.google.com/billing/01DF70-456C51-E3241B/credits`), promo credits automatically offset 100% of eligible charges.

### Step 3: Hard Stop $0.01 / $0.00 Budget Cap
Set a budget alert at `https://console.cloud.google.com/billing/01DF70-456C51-E3241B/budgets`:
- Target: $1.00 or $0.01
- Action: Automated Webhook or immediate gcloud unlink if credit burn approaches 0.

### Step 4: Instant Teardown After Demo
The moment the demo is finished, run:
```bash
gcloud billing projects unlink <PROJECT_ID>
```
This freezes the API calls and guarantees zero background leakage.
