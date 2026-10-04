UPDATE `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records`
SET non_profiteers_index = ARRAY_CONCAT(IFNULL(non_profiteers_index, []), [
  STRUCT("NPI-NWCDC-NEWARK" AS npi_id, "Newark Watershed Conservation (NWCDC)" AS organization_name, "FRAUD-KICKBACKS-BRIBERY" AS cms_billing_code, 0.00 AS unaccounted_fund_delta)
])
WHERE state_code = 'NJ';
