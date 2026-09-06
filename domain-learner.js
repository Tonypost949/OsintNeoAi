/**
 * Domain Pattern Learner & Smart Ingestion Engine for OsintNeoAi Extension.
 * Detects IRS 990s, USASpending grants, SOS entity filings, and Assessor portals.
 */

class DomainLearner {
  constructor() {
    this.hostname = window.location.hostname;
    this.path = window.location.pathname;
  }

  detectPortalType() {
    if (this.hostname.includes("propublica.org") || this.hostname.includes("guidestar.org") || document.body.innerText.includes("Form 990")) {
      return "NON_PROFIT_IRS_990";
    }
    if (this.hostname.includes("usaspending.gov") || this.hostname.includes("sam.gov")) {
      return "FEDERAL_GRANT_RECORD";
    }
    if (this.hostname.includes("sec.gov") || document.body.innerText.includes("Articles of Organization")) {
      return "BUSINESS_ENTITY_FILING";
    }
    return "GENERIC_PUBLIC_RECORD";
  }

  extractSmartData() {
    const portalType = this.detectPortalType();
    const extracted = {
      portalType,
      url: window.location.href,
      title: document.title,
      timestamp: new Date().toISOString(),
      entities: []
    };

    const text = document.body.innerText;

    // Extract EIN (Employer Identification Number)
    const einMatch = text.match(/\b\d{2}-\d{7}\b/g);
    if (einMatch) extracted.entities.push(...einMatch.map(e => ({ type: "EIN", value: e })));

    // Extract Dollar Amounts (Grants / Tax Exemptions / Executive Pay)
    const dollarMatch = text.match(/\$\s?[0-9,]{4,12}/g);
    if (dollarMatch) extracted.entities.push(...dollarMatch.slice(0, 10).map(d => ({ type: "FINANCIAL_AMOUNT", value: d })));

    return extracted;
  }
}

// Global hook for extension sidepanel
window.domainLearner = new DomainLearner();
