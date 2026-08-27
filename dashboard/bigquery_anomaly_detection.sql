-- ==============================================================================
-- PIPELINE 2: PPP & REAL ESTATE FRAUD ANOMALY DETECTION (TimesFM 2.5)
-- Target Project: noble-beanbag-497411-m4
-- Dataset: forensic_layers
-- ==============================================================================

WITH ppp_time_series AS (
  SELECT
    COALESCE(apn, 'UNASSIGNED_APN') AS apn_cluster,
    SAFE.PARSE_DATE('%m/%d/%Y', ppp_loan_1_date) AS disbursement_date,
    SUM(CAST(ppp_loan_1_amount AS FLOAT64)) AS total_disbursed,
    COUNT(1) AS loan_count
  FROM
    
oble-beanbag-497411-m4.forensic_layers.ppp_loans
  WHERE
    ppp_loan_1_date IS NOT NULL
    AND SAFE.PARSE_DATE('%m/%d/%Y', ppp_loan_1_date) IS NOT NULL
  GROUP BY
    apn_cluster, disbursement_date
)
SELECT
  apn_cluster,
  time_series_timestamp AS anomaly_timestamp,
  time_series_data AS disbursed_amount,
  ROUND(lower_bound, 2) AS expected_lower_bound,
  ROUND(upper_bound, 2) AS expected_upper_bound,
  ROUND(anomaly_probability, 4) AS anomaly_probability,
  is_anomaly
FROM
  AI.DETECT_ANOMALIES(
    (SELECT * FROM ppp_time_series WHERE disbursement_date <= DATE('2020-06-30')),
    (SELECT * FROM ppp_time_series WHERE disbursement_date > DATE('2020-06-30')),
    data_col => 'total_disbursed',
    timestamp_col => 'disbursement_date',
    id_cols => ['apn_cluster'],
    model => 'TimesFM 2.5',
    anomaly_prob_threshold => 0.85
  )
WHERE
  is_anomaly = TRUE
ORDER BY
  anomaly_probability DESC;
