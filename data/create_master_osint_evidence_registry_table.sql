-- BigQuery Table DDL for Master OSINT Evidence Registry (199 Records)
-- Target: noble-beanbag-497411-m4.national_audits.master_osint_evidence_registry

CREATE TABLE IF NOT EXISTS `noble-beanbag-497411-m4.national_audits.master_osint_evidence_registry` (
    Record_ID STRING NOT NULL OPTIONS(description="Unique record identifier (NODE, FCA, TGT, BQ, AUD, AST)"),
    Date_Documented STRING OPTIONS(description="Date documented or last verified"),
    Entity_Or_Subject STRING OPTIONS(description="Primary entity name, individual, or target subject"),
    Category STRING OPTIONS(description="Primary category classification"),
    Subcategory STRING OPTIONS(description="Secondary detailed category"),
    Role_Or_Classification STRING OPTIONS(description="Role, title, or classification level"),
    Primary_Identifier_Or_Email STRING OPTIONS(description="Primary email, domain, or identifier"),
    Linked_Accounts_Or_Entities STRING OPTIONS(description="Associated accounts, dockets, or linked entities"),
    Jurisdiction_Or_Location STRING OPTIONS(description="Jurisdiction, court, or cloud platform"),
    Legal_Statute_Or_Basis STRING OPTIONS(description="Legal basis, statute (FCA, RICO, Rules of Evidence)"),
    Evidence_SHA256_Hash STRING OPTIONS(description="Cryptographic SHA-256 evidence hash"),
    Verification_Status STRING OPTIONS(description="Verification or operational status"),
    Threat_Or_Impact_Level STRING OPTIONS(description="Threat or impact classification"),
    Source_Reference_File STRING OPTIONS(description="Provenance source file path"),
    Detailed_Forensic_Notes STRING OPTIONS(description="Full forensic notes and whistleblower narrative")
)
OPTIONS(
    description="Authoritative master OSINT evidence clearinghouse and entity registry for OsintNeoAi",
    labels=[("project", "osintneoai"), ("classification", "master_registry"), ("environment", "production")]
);
