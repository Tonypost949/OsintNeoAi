# PPP Loan Data — 11770 Warner Ave, Fountain Valley, CA 92708

## What This Is

Filtered SBA Paycheck Protection Program (PPP) loan data for all entities registered at **11770 Warner Ave, Fountain Valley, CA 92708**.

Source: [SBA PPP FOIA Public Dataset](https://data.sba.gov/dataset/ppp-foia) (September 2024 release)

## Files

| File | Description |
|------|-------------|
| `ppp_11770_warner.csv` | Filtered PPP loan records (18 rows) |
| `ppp_11770_warner_bq.json` | Newline-delimited JSON for BigQuery import |
| `ppp_bq_schema.json` | BigQuery table schema definition |
| `load_to_bigquery.sh` | One-command BigQuery load script |

## Summary

- **18 loans** across 16 unique entities
- **Total loan amount:** $1,112,211.96
- **Total forgiveness:** $1,108,811.84 (99.7% forgiveness rate)
- **Date range:** April 2020 – March 2021

## How to Load into BigQuery

```bash
# Authenticate first (one-time)
gcloud auth login

# Then run:
./load_to_bigquery.sh
```

Target table: `noble-beanbag-497411-m4:ppp_rico.ppp_11770_warner`

## Red Flags

1. **Multiple hospice/healthcare entities at one small office address** — 6 healthcare/hospice entities totaling $912,482 in loans from the same building
2. **Duplicate borrowers with slight name variations:**
   - MYDIEM HONG / MY DIEM T HONG (Suite 119) — two loans, $41,666 total
   - MORECARE PALLIATIVE & HOSPICE INC (Suite 210) — two loans, $625,000 total
   - WALLACE L CHOW, CPA / WALLACE CHOW (Suite 221) — two loans, $9,998 total
   - HOUGH CHIROPRACTIC, INC / HOUGH CHIROPRACTIC INC. (Suite 122) — two loans, $41,050 total
3. **99.7% forgiveness rate** — nearly every loan forgiven in full (15 of 18 received MORE than they borrowed)
4. **9 entities reported only 1 employee** yet received loans
5. **4 "new businesses" (≤2 years old)** received $101,742 combined
6. **INGRAM AMERICA LLC** — NAICS code 999990 (unclassified), new business, 3 employees, $36,402 loan
7. **Concentration pattern** — multiple healthcare entities at the same suite building is a documented PPP fraud typology
