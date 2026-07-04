# OSINTNeoAiXXL Deployment & 50-State Baseline Walkthrough 🚀

We have deployed your brand new, independent XXL environment and updated the BigQuery database baseline.

## 🔗 Live URLs

1. **Original Extraction Terminal (XL)**:
   - URL: [https://osint-chat-ui-941890989638.us-west1.run.app](https://osint-chat-ui-941890989638.us-west1.run.app)
2. **New Independent XXL Terminal**:
   - URL: [https://osint-chat-ui-xxl-941890989638.us-west1.run.app](https://osint-chat-ui-xxl-941890989638.us-west1.run.app)

---

## 🛠️ Baseline Database Set for All 50 States

To ensure the extraction terminal is robust across the whole country, we executed a script to populate the database with baseline records for **all 50 US States** (adding the remaining 42 state records alongside the initial 8 states):

- **Table**: `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records`
- **Total State Coverage**: 50 States (AL, AK, AZ, AR, CA, CO, CT, DE, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ, NM, NY, NC, ND, OH, OK, OR, PA, RI, SC, SD, TN, TX, UT, VT, VA, WA, WV, WI, WY).

---

## 🔍 Huntington Beach & Investigation Ingestion

The terminal successfully queries and displays active investigation records (such as **Andrew Do**, **Newark Watershed**, and the **Mercy House / Huntington Beach Navigation Center** operational agreement).
