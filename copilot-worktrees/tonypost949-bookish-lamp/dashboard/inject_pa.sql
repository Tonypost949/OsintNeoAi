-- Insert PA row if it does not exist
INSERT INTO `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records` (state_code, non_profiteers_index)
VALUES ('PA', [
  STRUCT("V-PA-882" AS npi_id, "Sterling-Rivers Nominee LLC (PHL-2026-009) [Admin_Root_01]" AS organization_name, "PA-INV-7721 - Emergency Cyber Audit" AS cms_billing_code, 850000.00 AS unaccounted_fund_delta),
  STRUCT("V-PA-991" AS npi_id, "Sterling-Rivers Nominee LLC (PGH-2026-112) [Admin_Root_01]" AS organization_name, "PA-INV-7722 - Public Health Consulting" AS cms_billing_code, 420000.00 AS unaccounted_fund_delta),
  STRUCT("V-PA-004-A" AS npi_id, "Sterling-Rivers Nominee LLC (PHL-2026-022) [Admin_Root_01]" AS organization_name, "PA-INV-7723 - Software License Fee (Split A)" AS cms_billing_code, 47500.00 AS unaccounted_fund_delta),
  STRUCT("V-PA-004-B" AS npi_id, "Sterling-Rivers Nominee LLC (PHL-2026-022) [Admin_Root_01]" AS organization_name, "PA-INV-7724 - Software License Fee (Split B)" AS cms_billing_code, 47500.00 AS unaccounted_fund_delta),
  STRUCT("V-PA-005-A" AS npi_id, "Sterling-Rivers Nominee LLC (PGH-2026-140) [Admin_Root_01]" AS organization_name, "PA-INV-7725 - Software License Fee (Split A)" AS cms_billing_code, 47500.00 AS unaccounted_fund_delta),
  STRUCT("V-PA-005-B" AS npi_id, "Sterling-Rivers Nominee LLC (PGH-2026-140) [Admin_Root_01]" AS organization_name, "PA-INV-7726 - Software License Fee (Split B)" AS cms_billing_code, 47500.00 AS unaccounted_fund_delta)
]);
