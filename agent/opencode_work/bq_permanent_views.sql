-- ====== v_7561_center_ave_cluster ======

    CREATE OR REPLACE VIEW `project-743aab84-f9a5-4ec7-954.ppp_rico.v_7561_center_ave_cluster` AS
    -- All entities linked to 7561 Center Ave, Huntington Beach commercial park
    WITH llcs_at_7561 AS (
        SELECT *
        FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
        WHERE UPPER(SiteAddress) LIKE '%7561%CENTER%'
           OR UPPER(MailAddress) LIKE '%7561%CENTER%'
    ),
    ppp_matches AS (
        SELECT 
            BorrowerName, BorrowerCity, BorrowerState,
            CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
            BusinessType, NAICSCode, NonProfit, JobsReported,
            ServicingLenderName, OriginatingLender,
            UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
        FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
        UNION ALL
        SELECT 
            BorrowerName, BorrowerCity, BorrowerState,
            CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
            BusinessType, NAICSCode, NonProfit, JobsReported,
            ServicingLenderName, OriginatingLender,
            UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
        FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
    )
    SELECT 
        l.Owner1 AS llc_owner,
        l.SiteAddress AS property_address,
        l.MailAddress AS mailing_address,
        l.MailCity,
        l.APN,
        l.LastSeller,
        l.LastSaleDate,
        l.LastSaleValue AS sale_price,
        p.BorrowerName AS ppp_borrower,
        p.BorrowerCity AS ppp_city,
        p.BorrowerState AS ppp_state,
        p.CurrentApprovalAmount AS ppp_amount,
        p.ForgivenessAmount AS ppp_forgiven,
        p.DateApproved AS ppp_approval_date,
        p.LoanStatus AS ppp_status,
        p.BusinessType,
        p.NAICSCode,
        p.ServicingLenderName AS ppp_lender,
        '7561 Center Ave, Huntington Beach' AS proximity_cluster
    FROM llcs_at_7561 l
    LEFT JOIN ppp_matches p 
        ON UPPER(REGEXP_REPLACE(l.Owner1, r'[-.,&/() ]', '')) = p.clean_name
    ;

-- ====== v_beach_blvd_contamination_zone ======

    CREATE OR REPLACE VIEW `project-743aab84-f9a5-4ec7-954.ppp_rico.v_beach_blvd_contamination_zone` AS
    -- LLCs and PPP entities within 0.5 mile of 17642 Beach Blvd (HBNC footprint)
    -- Addresses: 17642 Beach Blvd, 17631 Cameron Ln, 17472 Beach Blvd (G&M Oil #124)
    WITH zone_llcs AS (
        SELECT *
        FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
        WHERE UPPER(SiteAddress) LIKE '%17642%BEACH%'
           OR UPPER(SiteAddress) LIKE '%17472%BEACH%'
           OR UPPER(SiteAddress) LIKE '%17631%CAMERON%'
           OR UPPER(SiteAddress) LIKE '%17642%CAMERON%'
           OR UPPER(SiteAddress) LIKE '%17501%BEACH%'
           OR UPPER(SiteAddress) LIKE '%17721%BEACH%'
           OR UPPER(MailAddress) LIKE '%17642%BEACH%'
           OR UPPER(MailAddress) LIKE '%17472%BEACH%'
           OR UPPER(MailAddress) LIKE '%Cameron%'
    ),
    ppp_all AS (
        SELECT 
            BorrowerName, BorrowerCity, BorrowerState,
            CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
            BusinessType, NAICSCode, NonProfit, JobsReported,
            ServicingLenderName,
            UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
        FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
        UNION ALL
        SELECT 
            BorrowerName, BorrowerCity, BorrowerState,
            CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
            BusinessType, NAICSCode, NonProfit, JobsReported,
            ServicingLenderName,
            UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
        FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
    )
    SELECT 
        l.Owner1 AS llc_owner,
        l.SiteAddress AS property_address,
        l.MailAddress AS mailing_address,
        l.APN,
        l.LastSeller,
        l.LastSaleDate,
        l.LastSaleValue AS sale_price,
        p.BorrowerName AS ppp_borrower,
        p.BorrowerCity AS ppp_city,
        p.BorrowerState AS ppp_state,
        p.CurrentApprovalAmount AS ppp_amount,
        p.ForgivenessAmount AS ppp_forgiven,
        p.DateApproved AS ppp_approval_date,
        p.LoanStatus AS ppp_status,
        p.NAICSCode,
        '17472-17642 Beach Blvd Contamination Zone' AS zone_label
    FROM zone_llcs l
    LEFT JOIN ppp_all p 
        ON UPPER(REGEXP_REPLACE(l.Owner1, r'[-.,&/() ]', '')) = p.clean_name
    ;

-- ====== v_mailbox_cluster_hubs ======

    CREATE OR REPLACE VIEW `project-743aab84-f9a5-4ec7-954.ppp_rico.v_mailbox_cluster_hubs` AS
    -- CMRA hubs with 3+ LLCs, aggregated with PPP enrichment
    WITH mailbox_stats AS (
        SELECT 
            MailAddress,
            COUNT(*) AS llc_count,
            ROUND(AVG(SAFE_CAST(LastSaleValue AS FLOAT64)), 0) AS avg_sale_value,
            MIN(LastSaleDate) AS first_sale,
            MAX(LastSaleDate) AS last_sale,
            STRING_AGG(DISTINCT Owner1, ' | ' ORDER BY Owner1) AS llc_names,
            STRING_AGG(DISTINCT APN, '; ') AS apns
        FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
        WHERE MailAddress IS NOT NULL 
          AND MailAddress != ''
        GROUP BY MailAddress
        HAVING COUNT(*) >= 3
    )
    SELECT 
        m.MailAddress,
        m.llc_count,
        m.avg_sale_value,
        m.first_sale,
        m.last_sale,
        m.llc_names,
        m.apns,
        -- Risk flags
        CASE 
            WHEN m.llc_count >= 50 THEN 'CRITICAL'
            WHEN m.llc_count >= 20 THEN 'HIGH'
            WHEN m.llc_count >= 10 THEN 'MODERATE'
            ELSE 'MONITOR'
        END AS risk_level,
        CASE
            WHEN m.MailAddress LIKE '%1077%PACIFIC%COAST%' THEN 'Stewart Industries CMRA (PPE fraud)'
            WHEN m.MailAddress LIKE '%14752%BEACH%' THEN 'Beach Blvd commercial hub'
            WHEN m.MailAddress LIKE '%11770%WARNER%' THEN 'Major CMRA hub (60+ LLCs)'
            WHEN m.MailAddress LIKE '%NEWPORT%CENTER%' THEN 'Newport Center financial cluster'
            WHEN m.MailAddress LIKE '%17272%NEWHOPE%' THEN 'Fountain Valley industrial cluster'
            WHEN m.MailAddress LIKE '%PO BOX%' THEN 'USPS PO Box network'
            ELSE NULL
        END AS cluster_notes
    FROM mailbox_stats m
    ORDER BY m.llc_count DESC
    ;

-- ====== v_nonprofit_board_ppp_self_dealing ======

    CREATE OR REPLACE VIEW `project-743aab84-f9a5-4ec7-954.ppp_rico.v_nonprofit_board_ppp_self_dealing` AS
    -- Board members whose vendor companies received PPP
    SELECT 
        'MLADEN BUNTICH' AS board_member,
        'Mercy House Living Centers' AS nonprofit,
        'Buntich Construction' AS vendor_entity,
        'MLADEN BUNTICH CONSTR. CO. INC' AS ppp_borrower_name,
        1582217.00 AS ppp_amount,
        0 AS ppp_forgiven,
        'Upland, CA' AS ppp_location,
        'Paid in Full' AS ppp_status,
        'IRC 4941 Self-Dealing' AS legal_exposure,
        'meli-document-mercy-house-board-conflicts-of-interest (2).docx' AS source_doc
    UNION ALL
    SELECT 
        'BRYAN PAVALKO', 'Mercy House Living Centers', 'RBA Builders LLC',
        'RBA BUILDERS, INC.', 2590445.00, 0, 'Huntington Beach, CA', 'Paid in Full',
        'IRC 4941 Self-Dealing',
        'meli-document-mercy-house-board-conflicts-of-interest (2).docx'
    UNION ALL
    SELECT 
        'MIA BERGMAN', 'Mercy House Living Centers', 'Shopoff Realty Investments',
        'SHOPOFF REALTY INVESTMENTS LP', 2315294.00, 0, 'Irvine, CA', 'Paid in Full',
        'IRC 4941 Self-Dealing',
        'meli-document-mercy-house-board-conflicts-of-interest (2).docx'
    UNION ALL
    SELECT 
        'NATALIE MCCARTY', 'Mercy House Living Centers', 'Shopoff Realty Investments',
        'SHOPOFF REALTY INVESTMENTS LP', 2315294.00, 0, 'Irvine, CA', 'Paid in Full',
        'IRC 4941 Self-Dealing',
        'meli-document-mercy-house-board-conflicts-of-interest (2).docx'
    ;

-- ====== v_rico_enterprise_master ======

    CREATE OR REPLACE VIEW `project-743aab84-f9a5-4ec7-954.ppp_rico.v_rico_enterprise_master` AS
    -- Master join: HB LLCs + PPP + Environmental + Nonprofit connections
    WITH 
    llc_enriched AS (
        SELECT 
            Owner1, Owner2, SiteAddress, MailAddress, MailCity,
            APN, LastSeller, LastSaleDate, LastSaleValue,
            UPPER(REGEXP_REPLACE(Owner1, r'[-.,&/() ]', '')) AS clean_owner
        FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
    ),
    ppp_enriched AS (
        SELECT 
            BorrowerName, BorrowerCity, BorrowerState,
            CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
            BusinessType, NAICSCode, NonProfit, Gender, Veteran,
            JobsReported, ServicingLenderName, OriginatingLender,
            UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
        FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
        UNION ALL
        SELECT 
            BorrowerName, BorrowerCity, BorrowerState,
            CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
            BusinessType, NAICSCode, NonProfit, Gender, Veteran,
            JobsReported, ServicingLenderName, OriginatingLender,
            UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
        FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
    ),
    joined AS (
        SELECT 
            l.*,
            p.BorrowerName AS ppp_borrower,
            p.BorrowerCity AS ppp_city,
            p.BorrowerState AS ppp_state,
            p.CurrentApprovalAmount AS ppp_amount,
            p.ForgivenessAmount AS ppp_forgiven,
            p.DateApproved AS ppp_date,
            p.LoanStatus AS ppp_status,
            p.BusinessType,
            p.NAICSCode,
            p.NonProfit,
            p.JobsReported,
            p.ServicingLenderName AS lender,
            -- Proximity flags
            CASE 
                WHEN UPPER(l.SiteAddress) LIKE '%7561%CENTER%' 
                  OR UPPER(l.MailAddress) LIKE '%7561%CENTER%' 
                THEN '7561_CENTER_AVE'
                WHEN UPPER(l.SiteAddress) LIKE '%17642%BEACH%' 
                  OR UPPER(l.SiteAddress) LIKE '%17472%BEACH%'
                  OR UPPER(l.SiteAddress) LIKE '%CAMERON%LN%'
                THEN 'BEACH_BLVD_CONTAMINATION_ZONE'
                WHEN UPPER(l.SiteAddress) LIKE '%1077%PACIFIC%'
                  OR UPPER(l.MailAddress) LIKE '%1077%PACIFIC%'
                THEN 'STEWART_CMRA_HUB'
                WHEN UPPER(l.MailAddress) LIKE '%11770%WARNER%'
                THEN 'WARNER_AVE_CMRA_HUB'
                WHEN UPPER(l.MailAddress) LIKE '%NEWPORT%CENTER%'
                THEN 'NEWPORT_CENTER_CLUSTER'
                ELSE NULL
            END AS proximity_cluster,
            -- RICO risk tier
            CASE 
                WHEN p.CurrentApprovalAmount > 1000000 
                  AND UPPER(p.BorrowerCity) != UPPER(l.MailCity) 
                THEN 'TIER_1_CRITICAL'
                WHEN p.CurrentApprovalAmount > 500000 
                THEN 'TIER_2_HIGH'
                WHEN p.CurrentApprovalAmount > 150000
                  AND p.NonProfit = 'Y'
                THEN 'TIER_3_NONPROFIT_FLAG'
                ELSE 'TIER_4_MONITOR'
            END AS rico_risk_tier
        FROM llc_enriched l
        LEFT JOIN ppp_enriched p ON l.clean_owner = p.clean_name
    )
    SELECT * FROM joined
    WHERE ppp_borrower IS NOT NULL
    ;

