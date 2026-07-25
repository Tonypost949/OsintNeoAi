-- ============================================================================
-- HB OSINT FORENSIC: High-Risk Proximity Cross-Dataset Join
-- Project: noble-beanbag-497411-m4
-- Purpose: Link HB LLCs, PPP borrowers, and environmental sites by geo-location
-- ============================================================================

-- View 1: High-Risk Entities — PPP borrowers with HB property and UST proximity
CREATE OR REPLACE VIEW `noble-beanbag-497411-m4.forensic_views.high_risk_entities` AS
WITH hb_properties AS (
    SELECT 
        Owner1 AS owner_name,
        SiteAddress AS property_address,
        MailAddress AS mailing_address,
        MailCity AS mail_city,
        APN,
        LastSaleDate,
        LastSaleValue,
        -- Extract street number for geo-matching
        REGEXP_EXTRACT(SiteAddress, r'^(\d+)') AS street_number,
        REGEXP_REPLACE(SiteAddress, r'^\d+\s+', '') AS street_name
    FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
),
ppp_borrowers AS (
    SELECT 
        BorrowerName,
        BorrowerCity,
        BorrowerState,
        CurrentApprovalAmount,
        ForgivenessAmount,
        LoanStatus,
        DateApproved,
        JobsReported,
        NAICSCode,
        BusinessType,
        OriginatingLender,
        OriginatingLenderState
    FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
    UNION ALL
    SELECT 
        BorrowerName,
        BorrowerCity,
        BorrowerState,
        CurrentApprovalAmount,
        ForgivenessAmount,
        LoanStatus,
        DateApproved,
        JobsReported,
        NAICSCode,
        BusinessType,
        OriginatingLender,
        OriginatingLenderState
    FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
),
matched AS (
    SELECT 
        p.owner_name,
        p.property_address,
        p.mailing_address,
        p.mail_city,
        p.APN,
        p.LastSaleDate,
        p.LastSaleValue,
        l.BorrowerName,
        l.BorrowerCity AS ppp_city,
        l.BorrowerState AS ppp_state,
        l.CurrentApprovalAmount,
        l.ForgivenessAmount,
        l.LoanStatus,
        l.DateApproved,
        l.OriginatingLender,
        l.OriginatingLenderState,
        l.NAICSCode,
        l.BusinessType
    FROM hb_properties p
    INNER JOIN ppp_borrowers l 
        ON UPPER(REGEXP_REPLACE(p.owner_name, r'[^A-Z0-9]', '')) = 
           UPPER(REGEXP_REPLACE(l.BorrowerName, r'[^A-Z0-9]', ''))
    WHERE l.CurrentApprovalAmount > 0
)
SELECT * FROM matched;

-- View 2: UST Proximity — HB properties near known UST sites
CREATE OR REPLACE VIEW `noble-beanbag-497411-m4.forensic_views.ust_proximity` AS
SELECT 
    Owner1 AS owner_name,
    SiteAddress AS property_address,
    APN,
    LastSaleDate,
    LastSaleValue,
    MailAddress,
    MailCity,
    -- Flag if on Brookhurst corridor
    CASE WHEN UPPER(SiteAddress) LIKE '%BROOKHURST%' THEN TRUE ELSE FALSE END AS on_brookhurst_corridor,
    -- Flag if near Beach Blvd contamination
    CASE WHEN UPPER(SiteAddress) LIKE '%BEACH%BLVD%' 
         OR UPPER(SiteAddress) LIKE '%CAMERON%' THEN TRUE ELSE FALSE END AS near_beach_contamination
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE 
    UPPER(SiteAddress) LIKE '%BROOKHURST%'
    OR UPPER(SiteAddress) LIKE '%BEACH BLVD%'
    OR UPPER(SiteAddress) LIKE '%CAMERON%'
    OR UPPER(SiteAddress) LIKE '%CENTER AVE%'
    OR UPPER(APN) IN (
        '178-431-14',  -- 3311 Bounty Cir (Stewart)
        '151-234-09'   -- 21951 Brookhurst (Triumvirate)
    );

-- View 3: Cross-Layer Summary
CREATE OR REPLACE VIEW `noble-beanbag-497411-m4.forensic_views.cross_layer_summary` AS
SELECT 
    'PPP+Property' AS layer,
    COUNT(DISTINCT owner_name) AS entity_count,
    SUM(CurrentApprovalAmount) AS total_ppp,
    SUM(ForgivenessAmount) AS total_forgiven
FROM `noble-beanbag-497411-m4.forensic_views.high_risk_entities`
UNION ALL
SELECT 
    'UST Corridor' AS layer,
    COUNT(DISTINCT owner_name) AS entity_count,
    NULL AS total_ppp,
    NULL AS total_forgiven
FROM `noble-beanbag-497411-m4.forensic_views.ust_proximity`;

SELECT 'Views created in forensic_views dataset. Run: SELECT * FROM forensic_views.cross_layer_summary' AS status;
