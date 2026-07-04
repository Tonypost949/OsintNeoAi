# OSINT Entity Network Map — Huntington Beach RICO Investigation
## v2 — Three Pipelines

```mermaid
graph TD
    subgraph "PIPELINE 1: PPP → PROPERTY"
        direction LR
        SBA["SBA<br/>$3.1B OC PPP Loans"]-->L2T["L2T Media LLC<br/>$1.05M PPP"]
        SBA-->PREMIERE["Premiere Entertainment LLC<br/>$209K PPP"]
        L2T-->DYL["Dylan & Andrew Holdings LLC<br/>7561 Center Ave J1, HB<br/>$725K purchase (2022)"]
        PREMIERE-->STEWART["Stewart Industries LLC<br/>3311 Bounty Cir, Seal Beach<br/>$0 transfer (2021)"]
    end

    subgraph "PIPELINE 2: GRANT → TOXICS"
        direction TB
        HUD["HUD COC CA-600<br/>$155M PSH"]
        HHAP["State HHAP<br/>$14.6M+"]
        CO_ORANGE["County of Orange<br/>$36M+ contracts"]

        HUD-->OC_COC["OC Continuum of Care"]
        HHAP-->OC_COC
        CO_ORANGE-->OC_COC

        OC_COC-->HMIS["HMIS Database<br/>(211 OC / OC United Way)"]
        HMIS-->HBNC["HBNC Navigation Center<br/>17631 Cameron Ln, HB<br/>Operator: Mercy House"]
        HBNC-->TOXIC_SITE["TOXIC SITE<br/>17642 Beach Blvd<br/>Hex Cr-VI 49x EPA limit"]
    end

    subgraph "PIPELINE 3: CPS → TRAFFICKING"
        direction TB
        OC_SSA["OC Social Services Agency<br/>30,000 removals/yr"]
        OC_SSA-->|triggers| IVE["Federal Title IV-E<br/>$200M-$300M+/yr OC draw"]
        IVE-->PLACEMENT["Placement in shelter/group home"]
        PLACEMENT-->|referral via HMIS| HBNC
        HBNC-->DEATHS["4 Child Deaths<br/>279 Medical Emergencies"]
        OC_SSA-->ICWA_FRAUD["ICWA-IIM Fraud<br/>Theft from Native children's trusts"]
        DEATHS-.->|Qui Tam Evidence|TRAFFICKING_RING["Human Trafficking Ring<br/>$512M+ COVID Fraud"]
    end

    subgraph "NEXUS: Mercy House"
        MH["Mercy House Living Centers<br/>CEO: Larry Haynes"]
        HBNC-- operator -->MH
        
        subgraph "MH Financial Crimes"
            MW["FY23 Audit Finding<br/>Material Weakness"]
            SD["FY23 Audit Finding<br/>Significant Deficiency<br/>$1.5M revenue understatement"]
            ACLU_LAWSUIT["ACLU Lawsuit (2020)"]
            CM_CONTRACT_LOSS["Costa Mesa Contract Loss (2026)"]
            MH-.->MW
            MH-.->SD
            MH-.->ACLU_LAWSUIT
            MH-.->CM_CONTRACT_LOSS
        end
    end
    
    subgraph "Pham $0 Conveyance Layer"
        PETER["Peter Pham<br/>Indicted Fugitive"]-->CPC["CP Premier Capital LLC"]
        CPC-->CERRITOS["7100 Cerritos Ave<br/>$0 quitclaim"]
        CPC-->SHIRLEY["13801 Shirley St<br/>$0 quitclaim"]
    end

    L2T-.->TAM["Tam Nguyen<br/>Garden Grove CF"]
    PREMIERE-.->TAM
    DYL-.->PETER
    
    classDef pipeline fill:#333,color:#fff,stroke:#fff,stroke-width:2px;
    classDef nexus fill:#900,color:#fff,stroke:#fff,stroke-width:2px;
    classDef money fill:#0a0,color:#fff;
    classDef shell fill:#f90,color:#000;
    classDef person fill:#00f,color:#fff;
    classDef toxic fill:#f00,color:#fff,stroke:#f00,stroke-width:4px;
    classDef cps fill:#609,color:#fff;

    class SBA,HHAP,CO_ORANGE,IVE money;
    class L2T,PREMIERE,DYL,STEWART,CPC,CERRITOS,SHIRLEY shell;
    class TAM,PETER person;
    class OC_SSA,ICWA_FRAUD,DEATHS,TRAFFICKING_RING,PLACEMENT cps;
    class HBNC,MH nexus;
    class TOXIC_SITE toxic;
    
    classDef default fill:#eee,color:#000,stroke:#ccc;

```

## Entity Index

| ID | Type | Name | Role |
|----|------|------|------|
| PER-001 | Person | Anthony Michael DiMarcello III | Primary Investigator |
| PER-010 | Person | Peter Anh Pham | VAS founder; federal fugitive; 15 counts |
| PER-?? | Person | Tam Nguyen | Garden Grove Community Foundation President |
| PER-?? | Person | Larry Haynes | CEO, Mercy House |
| ORG_OC_SSA | CPS | OC Social Services Agency | Removal authority, IV-E billing |
| ORG_MERCY | Nonprofit | Mercy House Living Centers | Shelter operator, nexus of fraud |
| SHL-DAH | Shell | Dylan & Andrew Holdings LLC | 7561 Center Ave / PPP layer |
| PROP_HBNC | Toxic Site | 17631 Cameron Ln / 17642 Beach Blvd | Hex Cr-VI 49x EPA limit, child deaths |
| FUND_IV_E | Federal | Title IV-E Program | Per-diem funding for foster placement |
| EVID_CHILD_DEATHS | Evidence | 4 deaths + 279 emergencies | Documented at Mercy House facilities |
| CASE_ICWA | Fraud | ICWA-IIM Fraud Pattern | Alleged improper Native child removal |

---
*The above map is a working document and represents hypotheses under investigation based on available data. It is not a definitive statement of fact.*
