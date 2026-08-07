WITH state_root AS (
  SELECT 
    state,
    state_name
  FROM 
    `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records`
  WHERE 
    state = 'CA'
),

audit_metrics AS (
  SELECT 
    r.state,
    audit.audit_id,
    audit.report_num,
    audit.taxpayer_funds_reviewed
  FROM 
    `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records` r,
    UNNEST(r.performance_audit_list) AS audit
  WHERE 
    audit.report_num = '2023-102.1'
),

non_profit_leakage AS (
  SELECT 
    r.state,
    npi.organization_name,
    npi.cms_billing_code,
    npi.unaccounted_fund_delta AS original_delta,
    `project-743aab84-f9a5-4ec7-954.national_audits.calculate_fund_leakage`(
      24000000000, 
      13700000000  
    ) AS calculated_leakage_delta
  FROM 
    `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records` r,
    UNNEST(r.non_profiteers_index) AS npi
  WHERE 
    UPPER(npi.organization_name) LIKE '%MERCY HOUSE%'
),

environmental_hazard AS (
  SELECT 
    r.state,
    env.site_id,
    env.location_name,
    env.contaminant_type,
    env.test_multiplier,
    env.closure_status
  FROM 
    `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records` r,
    UNNEST(r.environmental_site_assessments) AS env
  WHERE 
    UPPER(env.location_name) LIKE '%HUNTINGTON BEACH%'
    AND env.contaminant_type = 'Hexavalent Chromium / CrVI'
)

SELECT 
  sr.state_name,
  am.report_num AS target_audit,
  am.taxpayer_funds_reviewed AS audit_scope_usd,
  npl.organization_name,
  npl.cms_billing_code,
  npl.calculated_leakage_delta AS calculated_unaccounted_usd,
  eh.location_name AS toxic_site_name,
  eh.contaminant_type,
  eh.test_multiplier AS safety_limit_exceedance_multiplier,
  eh.closure_status AS geotracker_disputed_status
FROM 
  state_root sr
JOIN 
  audit_metrics am ON sr.state = am.state
JOIN 
  non_profit_leakage npl ON sr.state = npl.state
JOIN 
  environmental_hazard eh ON sr.state = eh.state;
