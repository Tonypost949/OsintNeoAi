SELECT a.state, env.location_name, env.contaminant_type, env.test_multiplier 
FROM `noble-beanbag-497411-m4.national_audits.all_state_records` a, 
UNNEST(a.environmental_site_assessments) env 
WHERE LOWER(env.location_name) LIKE '%huntington%' OR LOWER(env.location_name) LIKE '%beach%';
