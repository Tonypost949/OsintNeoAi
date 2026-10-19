/**
 * domain-learner.js — Smart Domain-Aware Ingestion Engine
 *
 * Automatically detects page types on government & non-profit portals:
 * - IRS Form 990 / ProPublica / Guidestar
 * - State SOS / Business Registries
 * - County Assessor / Property Portals
 * - USASpending.gov / Federal Grant Portals
 *
 * Extracts structured entities and pipes to workspace knowledge graph.
 */

const DOMAIN_PATTERNS = {
  "irs.gov": {
    type: "IRS_Form_990",
    selectors: {
      ein: '[data-field="ein"], .ein-number',
      revenue: '[data-field="total_revenue"]',
      expenses: '[data-field="total_expenses"]',
      compensation: '[data-field="officer_compensation"]',
      programExpenses: '[data-field="program_service_expenses"]',
    },
  },
  "propublica.org": {
    type: "ProPublica_NonProfit",
    selectors: {
      ein: ".ein",
      revenue: ".total-revenue",
      expenses: ".total-expenses",
      compensation: ".officer-compensation",
      name: ".organization-name",
    },
  },
  "usaspending.gov": {
    type: "Federal_Grants",
    selectors: {
      awardId: '[data-testid="award-id"]',
      recipient: '[data-testid="recipient-name"]',
      amount: '[data-testid="award-amount"]',
      agency: '[data-testid="awarding-agency"]',
      description: '[data-testid="award-description"]',
    },
  },
  "sam.gov": {
    type: "SAM_Gov_Entity",
    selectors: {
      legalName: "#legalBusinessName",
      ein: "#ein",
      uei: "#uei",
      status: "#registrationStatus",
    },
  },
  "county assessor": {
    type: "Property_Records",
    selectors: {
      parcelId: ".parcel-id, [data-field='parcel']",
      value: ".assessed-value, [data-field='assessed_value']",
      owner: ".owner-name, [data-field='owner']",
      address: ".property-address",
    },
  },
};

const RED_FLAG_HEURISTICS = {
  highAdminRatio: (data) => {
    if (data.adminExpenses && data.programExpenses) {
      const ratio = data.adminExpenses / (data.adminExpenses + data.programExpenses);
      return ratio > 0.35 ? { flag: true, severity: "HIGH", message: `Administrative expense ratio: ${(ratio * 100).toFixed(1)}% (threshold: 35%)` } : { flag: false };
    }
    return { flag: false };
  },
  excessiveCompensation: (data) => {
    if (data.compensation && data.revenue && data.compensation / data.revenue > 0.1) {
      return { flag: true, severity: "MEDIUM", message: `Executive compensation exceeds 10% of revenue` };
    }
    return { flag: false };
  },
  lowProgramSpending: (data) => {
    if (data.programExpenses && data.revenue && data.programExpenses / data.revenue < 0.5) {
      return { flag: true, severity: "HIGH", message: `Program spending below 50% of revenue` };
    }
    return { flag: false };
  },
};

class DomainLearner {
  constructor() {
    this.extractedEntities = [];
    this.learnedPatterns = {};
    this.redFlags = [];
  }

  detectPageType(url, title) {
    const hostname = new URL(url).hostname.toLowerCase();
    for (const [domain, config] of Object.entries(DOMAIN_PATTERNS)) {
      if (hostname.includes(domain) || (title && title.toLowerCase().includes(domain))) {
        return config;
      }
    }
    return { type: "generic", selectors: {} };
  }

  extractEntities(document) {
    const entities = [];
    const url = window.location.href;
    const title = document.title;
    const pageConfig = this.detectPageType(url, title);

    if (pageConfig.type === "generic") {
      const jsonLd = document.querySelectorAll('script[type="application/ld+json"]');
      jsonLd.forEach((script) => {
        try {
          const data = JSON.parse(script.textContent);
          if (data["@type"]) entities.push({ type: data["@type"], data });
        } catch (e) {}
      });
    } else {
      for (const [field, selector] of Object.entries(pageConfig.selectors)) {
        const el = document.querySelector(selector);
        if (el) {
          entities.push({ field, value: el.textContent.trim(), source: pageConfig.type });
        }
      }
    }

    this.extractedEntities = entities;
    return entities;
  }

  analyzeRedFlags(data) {
    this.redFlags = [];
    for (const [name, check] of Object.entries(RED_FLAG_HEURISTICS)) {
      const result = check(data);
      if (result.flag) {
        this.redFlags.push({ heuristic: name, ...result });
      }
    }
    return this.redFlags;
  }

  learnPattern(domain, selector, fieldName) {
    if (!this.learnedPatterns[domain]) this.learnedPatterns[domain] = {};
    this.learnedPatterns[domain][fieldName] = selector;
  }

  getKnowledgeGraphNodes() {
    return this.extractedEntities.map((e) => ({
      id: `${e.type || e.field}-${Date.now()}`,
      type: e.type || e.field,
      value: e.value || e.data,
      source: window.location.href,
      timestamp: new Date().toISOString(),
    }));
  }
}

if (typeof window !== "undefined") {
  window.DomainLearner = DomainLearner;
}
