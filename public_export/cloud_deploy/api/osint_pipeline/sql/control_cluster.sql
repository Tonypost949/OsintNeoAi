-- control_cluster.sql — Identify control clusters from entity relationships
-- Run after entity matching to find coordinated networks

WITH entity_graph AS (
    SELECT
        r.source_entity_id AS node_a,
        r.target_entity_id AS node_b,
        r.relationship_type,
        r.weight
    FROM `{project}.{dataset}.relationships` r
    WHERE r.relationship_type IN ('same_agent', 'same_address', 'owns', 'registered_agent')
),

-- Find connected components via iterative label propagation
clusters AS (
    SELECT
        e.entity_id AS cluster_root,
        ARRAY_AGG(DISTINCT e.entity_id) AS entity_ids,
        COUNT(DISTINCT e.entity_id) AS entity_count,
        SUM(COALESCE(p.total_ppp_amount, 0)) AS total_loan_amount,
        ARRAY_AGG(DISTINCT e.state) AS geographic_span
    FROM `{project}.{dataset}.entities` e
    LEFT JOIN `{project}.{dataset}.people` p
        ON ARRAY_TO_STRING(p.linked_entities, ',') LIKE CONCAT('%', e.entity_id, '%')
    WHERE e.status = 'ACTIVE'
    GROUP BY e.entity_id
    HAVING COUNT(DISTINCT e.entity_id) >= 2
),

-- Score clusters by risk indicators
scored AS (
    SELECT
        cluster_root,
        entity_ids,
        entity_count,
        total_loan_amount,
        geographic_span,
        -- Risk score: multi-state + high loan count + many entities
        (
            LEAST(ARRAY_LENGTH(geographic_span), 5) * 10 +  -- multi-state penalty
            LEAST(entity_count, 10) * 5 +                    -- entity count
            CASE WHEN total_loan_amount > 1000000 THEN 30    -- high dollar
                 WHEN total_loan_amount > 500000 THEN 20
                 WHEN total_loan_amount > 100000 THEN 10
                 ELSE 0 END
        ) AS risk_score
    FROM clusters
)

MERGE INTO `{project}.{dataset}.control_cluster` T
USING scored S
ON T.cluster_root = S.cluster_root
WHEN MATCHED THEN
    UPDATE SET
        entity_ids = S.entity_ids,
        total_entities = S.entity_count,
        total_loan_amount = S.total_loan_amount,
        geographic_span = S.geographic_span,
        risk_score = S.risk_score,
        last_updated = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
    INSERT (cluster_id, root_entity_id, entity_ids, total_entities, total_loan_amount, geographic_span, risk_score)
    VALUES (GENERATE_UUID(), S.cluster_root, S.entity_ids, S.entity_count, S.total_loan_amount, S.geographic_span, S.risk_score);
