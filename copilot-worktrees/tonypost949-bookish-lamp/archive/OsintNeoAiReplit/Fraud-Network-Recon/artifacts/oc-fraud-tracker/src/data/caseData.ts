export type LegalStatus =
  | "convicted"
  | "indicted"
  | "fugitive"
  | "civil_defendant"
  | "unnamed_individual"
  | "not_charged";

export type ActorTier =
  | "primary"
  | "do_family"
  | "h2h_officers"
  | "government_enablers"
  | "church_layer"
  | "unidentified";

export interface Actor {
  id: string;
  name: string;
  role: string;
  organization?: string;
  status: LegalStatus;
  tier: ActorTier;
  statusDetail: string;
  crimes?: string[];
  connections: string[];
  indictmentDesignation?: string;
  notes?: string;
}

export interface Entity {
  id: string;
  name: string;
  type: "nonprofit" | "shell_company" | "restaurant" | "government" | "church" | "real_estate" | "unknown";
  role: string;
  fundsReceived?: string;
  fundsDirection?: string;
  relatedActors: string[];
  notes?: string;
}

export interface TimelineEvent {
  date: string;
  sortKey: string;
  event: string;
  category: "contract" | "crime" | "investigation" | "legal" | "flight" | "other";
  actors?: string[];
  amount?: string;
}

export interface MoneyFlow {
  from: string;
  to: string;
  amount: string;
  description: string;
  legalCharge?: string;
}

export interface OutstandingQuestion {
  id: string;
  question: string;
  context: string;
  relatedActors?: string[];
}

export const CASE_SUMMARY = {
  title: "Orange County COVID Relief Fraud",
  caseNumber: "8:25-CR-00100-JVS (Central District of California)",
  totalStolen: "$12–13.5 million",
  fundSource: "CARES Act + ARPA (American Rescue Plan Act)",
  fraudMechanism:
    "Systematic looting through shell nonprofits, fabricated meal-delivery contracts, and bribery of an elected Orange County Supervisor. Not a dollar's worth of meals was ever properly documented as delivered.",
  primarySources: [
    "Federal Indictment 8:25-CR-00100-JVS (Central District of California)",
    "OC County First Amended Complaint ROA45 (San Diego Superior Court)",
    "LAist investigative reporting",
    "OC Register, Voice of OC",
    "CA Secretary of State public filings",
    "IRS Form 990 public filings",
    "Transparent California salary database",
  ],
  compiledDate: "March 31, 2026",
};

export const ACTORS: Actor[] = [
  {
    id: "andrew-do",
    name: "Andrew Hoang Do",
    role: "OC Board of Supervisors, District 1 (2015–Oct 2024)",
    organization: "Orange County Board of Supervisors",
    status: "convicted",
    tier: "primary",
    statusDetail:
      "Pleaded guilty October 22, 2024. Sentenced 5 years federal prison.",
    crimes: [
      "Conspiracy to commit bribery",
      "Accepted $550,000–$730,500 in bribes funneled through VAS to his daughters",
      "Personally edited contract terms to remove meal delivery minimums and accountability provisions",
      "Used unilateral discretionary fund authority to steer $13.5M+ to VAS and H2H without board votes or public disclosure",
    ],
    connections: [
      "peter-pham",
      "chris-wangsaporn",
      "cheri-pham",
      "rhiannon-do",
      "ilene-do",
      "viet-america-society",
      "hand-to-hand",
    ],
    notes:
      "Resigned the day of his guilty plea. His home was raided by federal agents on August 22, 2024.",
  },
  {
    id: "peter-pham",
    name: "Peter Anh Pham",
    role: "Founder and President, Viet America Society (VAS)",
    organization: "Viet America Society",
    status: "fugitive",
    tier: "primary",
    statusDetail:
      "15-count federal indictment (June 2025). Fled to Taipei, Taiwan on a one-way ticket December 2024. No extradition treaty between US and Taiwan.",
    crimes: [
      "Wire fraud",
      "Conspiracy",
      "Money laundering",
      "Bribery",
      "Created VAS 8 days after Andrew Do voted to allocate $1M in COVID funds",
      "Pocketed millions through personal checks",
      "Bought a Garden Grove residential property with fraud proceeds",
      "Funneled money through D Air, HD Construction, and Perfume River Restaurant",
    ],
    connections: [
      "andrew-do",
      "thu-thao-thi-vu",
      "viet-america-society",
      "d-air-conditioning",
      "hd-construction",
      "behavioral-health-solutions",
      "perfume-river",
    ],
    indictmentDesignation: "Named defendant (PHAM)",
  },
  {
    id: "thanh-huong-nguyen",
    name: "Thanh Huong Nguyen",
    role: "CEO/President, Hand to Hand Relief Organization (H2H)",
    organization: "Hand to Hand Relief Organization",
    status: "indicted",
    tier: "primary",
    statusDetail:
      "Federal charges: conspiracy to commit wire fraud, wire fraud, money laundering.",
    crimes: [
      "Signed 6 false invoices to OC for $1M claiming meals delivered",
      "Immediately looted $2M SLFRF contract upon receipt",
      "Paid $500K to Perfume River",
      "Paid $125K to HD Construction",
      "Paid $50K to D Air",
      "Paid $72K to STMM Real Estate for personal residence rent",
      "Hundreds of thousands in structured ATM cash withdrawals under $10K to evade IRS reporting",
    ],
    connections: [
      "michael-nguyen",
      "loc-nguyen",
      "tony-martin",
      "hand-to-hand",
      "perfume-river",
      "d-air-conditioning",
      "hd-construction",
      "stmm-real-estate",
      "angel-nail-spa",
    ],
    indictmentDesignation: "Named defendant (NGUYEN)",
    notes: "Also owns Quan Chay Tu Thien restaurant at 9098 Bolsa Ave, Westminster (same address as H2H).",
  },
  {
    id: "thu-thao-thi-vu",
    name: "Thu Thao Thi Vu",
    role: "President, Aloha Financial Investment Inc. dba Perfume River Restaurant & Lounge",
    organization: "Aloha Financial Investment Inc. / Perfume River",
    status: "civil_defendant",
    tier: "primary",
    statusDetail:
      "Named civil defendant in companion VAS case (OC v. VAS et al.).",
    crimes: [
      "Co-controlled primary money laundering conduit",
      "VAS paid Perfume River $100,000–$108,000/month (later $150K–$315K at a time)",
      "D Air funneled $25K checks through Perfume River back to Peter Pham and to Rhiannon Do",
    ],
    connections: ["peter-pham", "perfume-river", "d-air-conditioning", "rhiannon-do"],
    indictmentDesignation: "Individual #2 — associate of defendant PHAM who controlled Aloha Financial Investment / Perfume River",
    notes: "Perfume River restaurant is now shuttered.",
  },
  {
    id: "cheri-pham",
    name: "Cheri Pham",
    role: "OC Superior Court Assistant Presiding Judge; wife of Andrew Do",
    organization: "OC Superior Court",
    status: "not_charged",
    tier: "do_family",
    statusDetail:
      "Still a sitting judge as of last available reporting. No charges filed publicly.",
    connections: ["andrew-do", "rhiannon-do", "ilene-do"],
    notes:
      "Her home was raided by federal agents on August 22, 2024. The VAS and H2H lawsuits had to be filed in San Diego Superior Court specifically because Cheri Pham is an OC judge — conflicts of interest prevented filing in Orange County.",
  },
  {
    id: "rhiannon-do",
    name: "Rhiannon Do",
    role: "President of VAS; Andrew Do's younger daughter",
    organization: "Viet America Society",
    status: "civil_defendant",
    tier: "do_family",
    statusDetail:
      "Named civil defendant. Made deal with federal authorities to avoid prosecution. Home raided August 2024.",
    crimes: [
      "Received $8,000/month for 2+ years ($224,000 total) from Perfume River/Aloha Financial funded by VAS county money",
      "Received $381,500 wired to escrow to purchase a $1,035,000 home in Tustin, CA (July 2023) — confirmed bribe payment",
    ],
    connections: [
      "andrew-do",
      "peter-pham",
      "thu-thao-thi-vu",
      "viet-america-society",
      "perfume-river",
    ],
    indictmentDesignation: "Individual #5",
    notes:
      "Federal judge ordered forfeiture of the Tustin house. Millions returned to taxpayers.",
  },
  {
    id: "ilene-do",
    name: "Ilene Do",
    role: "Andrew Do's elder daughter; formerly HHS Inspector General analyst",
    organization: "Moulton Niguel Water District (at time of crime)",
    status: "not_charged",
    tier: "do_family",
    statusDetail:
      "Not publicly charged. Father's restitution covers the $100K she received.",
    crimes: [
      "Received four $25,000 checks = $100,000 total (three from D Air Conditioning, one directly from Peter Pham)",
      "Deposited to her Citibank account Sept–Oct 2022",
    ],
    connections: [
      "andrew-do",
      "peter-pham",
      "d-air-conditioning",
      "brian-probolsky",
    ],
    indictmentDesignation: "Individual #6",
    notes:
      "Previously worked at HHS Inspector General's office investigating healthcare fraud, then became a recipient of COVID fraud proceeds. Worked at Moulton Niguel Water District where Brian Probolsky sits on the board.",
  },
  {
    id: "loc-nguyen",
    name: "Loc Nguyen",
    role: "CFO/Treasurer of H2H",
    organization: "Hand to Hand Relief Organization",
    status: "civil_defendant",
    tier: "h2h_officers",
    statusDetail:
      "Named civil defendant, OC County v. H2H (filed San Diego Superior Court).",
    connections: ["thanh-huong-nguyen", "hand-to-hand"],
    indictmentDesignation:
      "Listed as CFO/Treasurer per CA Secretary of State filings",
  },
  {
    id: "michael-nguyen",
    name: "Michael Nguyen",
    role: "Secretary of H2H",
    organization: "Hand to Hand Relief Organization",
    status: "civil_defendant",
    tier: "h2h_officers",
    statusDetail:
      "Named civil defendant, OC County v. H2H (filed San Diego Superior Court).",
    crimes: [
      "Personally withdrew approximately $9,500 in cash multiple times per week throughout Jan-March 2023 after $2M county deposit",
      "Structured withdrawals to stay under $10K IRS reporting threshold (structuring/smurfing)",
      "Total: hundreds of thousands in structured cash withdrawals",
    ],
    connections: ["thanh-huong-nguyen", "hand-to-hand"],
    notes: "Documented withdrawals on 35+ separate occasions across Jan–March 2023.",
  },
  {
    id: "tony-martin",
    name: "Tony Martin",
    role: "Vice President of H2H",
    organization: "Hand to Hand Relief Organization",
    status: "not_charged",
    tier: "h2h_officers",
    statusDetail:
      "Listed in IRS Form 990 filings (tax years 2021 and 2022). Not yet named as a civil defendant in public filings reviewed.",
    connections: ["thanh-huong-nguyen", "hand-to-hand"],
  },
  {
    id: "chris-wangsaporn",
    name: "Chris Wangsaporn",
    role: "Chief of Staff to Andrew Do",
    organization: "Orange County Board of Supervisors",
    status: "unnamed_individual",
    tier: "government_enablers",
    statusDetail:
      "Resigned October 2024, the day after LAist published article about Josie Batres/$275K contract. Not publicly charged.",
    crimes: [
      "Processed paperwork for fraudulent contracts and grants",
      "Edited contract terms to benefit VAS and H2H",
      "Emailed county employees to create the $2M H2H SLFRF contract and the $3M VAS Senior Congregant Meal agreement",
    ],
    connections: ["andrew-do", "josie-batres", "viet-america-society", "hand-to-hand"],
    indictmentDesignation: "Individual #3 — Do's chief of staff at the County",
  },
  {
    id: "josie-batres",
    name: "Josie Batres",
    role: "Fiancée/wife of Chris Wangsaporn; owner of Talentgate Inc.",
    organization: "Talentgate, Inc.",
    status: "unnamed_individual",
    tier: "government_enablers",
    statusDetail:
      "Not publicly charged as of last reporting.",
    crimes: [
      "Received $10,000/month starting August 2020 from VAS funds under guise of consulting services",
      "Hired by Mind OC nonprofit for a $275,000 mental health contract at Andrew Do's direction; work never delivered; Mind OC refunded the money",
    ],
    connections: ["chris-wangsaporn", "andrew-do", "viet-america-society"],
    indictmentDesignation: "Individual #4",
  },
  {
    id: "brian-probolsky",
    name: "Brian Probolsky",
    role: "Andrew Do's earlier Chief of Staff; Moulton Niguel Water District board member; former CEO of OC Power Authority",
    organization: "Moulton Niguel Water District / OC Power Authority",
    status: "not_charged",
    tier: "government_enablers",
    statusDetail:
      "Won re-election to Moulton Niguel Water District board November 2024. Not charged.",
    connections: ["andrew-do", "ilene-do"],
    notes:
      "Appointed CEO of OC Power Authority (OCPA) with no competitive process and no energy experience; ousted in April 2023 after damning audits citing lack of transparency in contracting. Ilene Do worked at Moulton Niguel Water District where Probolsky sits on the board.",
  },
];

export const ENTITIES: Entity[] = [
  {
    id: "viet-america-society",
    name: "Viet America Society (VAS)",
    type: "nonprofit",
    role: "Primary fraudulent nonprofit through which Andrew Do funneled county COVID funds",
    fundsReceived: "$7.2M+ in county contracts",
    relatedActors: ["peter-pham", "rhiannon-do", "chris-wangsaporn"],
    notes:
      "Created by Peter Pham 8 days after Andrew Do voted to allocate $1M in COVID funds on June 2, 2020.",
  },
  {
    id: "hand-to-hand",
    name: "Hand to Hand Relief Organization (H2H)",
    type: "nonprofit",
    role: "Secondary fraudulent nonprofit; received $3M+ in COVID contracts; looted immediately",
    fundsReceived: "$3M+",
    relatedActors: [
      "thanh-huong-nguyen",
      "loc-nguyen",
      "michael-nguyen",
      "tony-martin",
    ],
    notes:
      "H2H's principal address at 9098 Bolsa Ave, Westminster is the same as Thanh Huong Nguyen's for-profit restaurant.",
  },
  {
    id: "perfume-river",
    name: "Perfume River Restaurant & Lounge / Aloha Financial Investment Inc.",
    type: "restaurant",
    role: "Primary money laundering conduit; funds cycled through it back to Peter Pham and Do daughters",
    fundsReceived: "$100K–$315K per transaction",
    relatedActors: ["thu-thao-thi-vu", "peter-pham", "rhiannon-do"],
    notes: "Now shuttered. VAS paid Perfume River $100,000–$108,000/month.",
  },
  {
    id: "d-air-conditioning",
    name: "D Air Conditioning Co. LLC",
    type: "shell_company",
    role: "Westminster HVAC company used as money laundering conduit; issued bribe checks to Ilene Do",
    fundsReceived: "$256,000+",
    relatedActors: ["ilene-do", "peter-pham"],
    notes:
      "Owner not publicly named. Received $256,000+ from VAS, AFI, and HD Construction. Issued four $25,000 checks to Ilene Do. Designated 'Company #2' in Andrew Do's plea.",
  },
  {
    id: "hd-construction",
    name: "HD Construction Inc.",
    type: "shell_company",
    role: "Secondary laundering conduit; received millions from VAS, AFI, and H2H",
    relatedActors: ["peter-pham", "thanh-huong-nguyen"],
    notes:
      "Owner: Le Dan Hua — named defendant in companion VAS civil case. On Jan 10, 2023, H2H wrote $125,000 check to HD Construction with memo 'Construction Restaurant' — charged as money laundering Count Fourteen.",
  },
  {
    id: "behavioral-health-solutions",
    name: "Behavioral Health Solutions LLC",
    type: "shell_company",
    role: "Peter Pham-controlled entity; received laundered VAS funds",
    fundsReceived: "$300,000+",
    relatedActors: ["peter-pham"],
    notes: "Received three $100,000 checks from VAS with memo 'Donation'.",
  },
  {
    id: "stmm-real-estate",
    name: "STMM Real Estate LLC",
    type: "real_estate",
    role: "Received COVID meal funds as personal rent payments for Thanh Huong Nguyen",
    fundsReceived: "$144,000",
    relatedActors: ["thanh-huong-nguyen"],
    notes:
      "Received $72,000 on Feb 1, 2023 (year 2022 rent) and $72,000 on Feb 10, 2023 (year 2023 rent). Owner connection not public.",
  },
  {
    id: "angel-nail-spa",
    name: "Angel Nail Spa",
    type: "shell_company",
    role: "Thanh Huong Nguyen's nail salon; received H2H COVID funds",
    fundsReceived: "$30,000",
    relatedActors: ["thanh-huong-nguyen"],
    notes:
      "Received $30,000 from H2H funds on Sept 14, 2020, listed as 'meals provided' in general ledger.",
  },
  {
    id: "talentgate",
    name: "Talentgate, Inc.",
    type: "shell_company",
    role: "Josie Batres' company; received $10K/month from VAS funds as fake consulting payments",
    relatedActors: ["josie-batres", "chris-wangsaporn"],
  },
];

export const TIMELINE: TimelineEvent[] = [
  {
    date: "June 2, 2020",
    sortKey: "2020-06-02",
    event: "Andrew Do votes to allocate $1M in COVID funds to his district",
    category: "contract",
    actors: ["andrew-do"],
    amount: "$1,000,000",
  },
  {
    date: "June 10, 2020",
    sortKey: "2020-06-10",
    event:
      "Peter Pham creates Viet America Society (VAS) — just 8 days after Do's vote",
    category: "crime",
    actors: ["peter-pham", "viet-america-society"],
  },
  {
    date: "July 17, 2020",
    sortKey: "2020-07-17",
    event: "H2H signs $1M CARES contract with Orange County",
    category: "contract",
    actors: ["thanh-huong-nguyen", "hand-to-hand"],
    amount: "$1,000,000",
  },
  {
    date: "Aug 2020 – Dec 2020",
    sortKey: "2020-08-01",
    event:
      "H2H submits 6 false invoices; receives $1M; immediately launders to VAS, AFI, Angel Nail Spa",
    category: "crime",
    actors: ["thanh-huong-nguyen", "hand-to-hand"],
    amount: "$1,000,000",
  },
  {
    date: "Aug 2020",
    sortKey: "2020-08-15",
    event:
      "Josie Batres (Individual #4) begins receiving $10,000/month from VAS funds as fake consulting payments",
    category: "crime",
    actors: ["josie-batres", "chris-wangsaporn"],
  },
  {
    date: "Jan 2021 – May 2022",
    sortKey: "2021-01-01",
    event:
      "VAS signs $200K then $4M in contracts; money flows to Pham, Batres, Thu Thao Thi Vu, Ilene Do",
    category: "crime",
    actors: ["andrew-do", "peter-pham", "viet-america-society"],
    amount: "$4,200,000",
  },
  {
    date: "Sept–Oct 2022",
    sortKey: "2022-09-15",
    event:
      "Ilene Do deposits four $25,000 checks from D Air Conditioning and Peter Pham into her Citibank account",
    category: "crime",
    actors: ["ilene-do", "d-air-conditioning", "peter-pham"],
    amount: "$100,000",
  },
  {
    date: "Sept 13, 2022",
    sortKey: "2022-09-13",
    event: "Board approves $6.9M discretionary fund for Do's district",
    category: "contract",
    actors: ["andrew-do"],
    amount: "$6,900,000",
  },
  {
    date: "Nov–Dec 2022",
    sortKey: "2022-11-01",
    event:
      "$2M H2H SLFRF contract executed; $2.2M VAS beneficiary agreement signed",
    category: "contract",
    actors: ["andrew-do", "chris-wangsaporn", "thanh-huong-nguyen"],
    amount: "$4,200,000",
  },
  {
    date: "Jan 3, 2023",
    sortKey: "2023-01-03",
    event: "$2M deposited to H2H — looting begins immediately",
    category: "crime",
    actors: ["thanh-huong-nguyen"],
    amount: "$2,000,000",
  },
  {
    date: "Jan 10, 2023",
    sortKey: "2023-01-10",
    event:
      "H2H issues: $500K to Perfume River, $125K to HD Construction, $50K to D Air, $50K to That No Group Corp, $50K to Chomobo Inc, $25K to Son Pham",
    category: "crime",
    actors: ["thanh-huong-nguyen", "hand-to-hand"],
    amount: "$800,000",
  },
  {
    date: "Jan–March 2023",
    sortKey: "2023-01-07",
    event:
      "Michael Nguyen conducts 35+ structured ATM withdrawals of $9,500 each to evade IRS reporting",
    category: "crime",
    actors: ["michael-nguyen"],
  },
  {
    date: "May 24, 2023",
    sortKey: "2023-05-24",
    event:
      "Anabel Garcia OCHCA HIPAA authorization form dated — church-based housing program recruitment",
    category: "other",
    actors: [],
  },
  {
    date: "July 2023",
    sortKey: "2023-07-01",
    event:
      "$381,500 wired from AFI/Perfume River to escrow for Rhiannon Do's $1,035,000 home in Tustin, CA",
    category: "crime",
    actors: ["rhiannon-do", "thu-thao-thi-vu", "peter-pham"],
    amount: "$381,500",
  },
  {
    date: "Aug 11, 2023",
    sortKey: "2023-08-11",
    event: 'VAS signs $3M "Senior Congregant Meal Program" agreement',
    category: "contract",
    actors: ["andrew-do", "peter-pham", "viet-america-society"],
    amount: "$3,000,000",
  },
  {
    date: "Aug 18, 2023",
    sortKey: "2023-08-18",
    event: "$3M wired to VAS — moved to VAS Account 3, sits untouched",
    category: "crime",
    actors: ["peter-pham", "viet-america-society"],
    amount: "$3,000,000",
  },
  {
    date: "Aug 22, 2024",
    sortKey: "2024-08-22",
    event:
      "FBI raids Andrew Do, Rhiannon Do, and Cheri Pham home; simultaneous raid on Peter Pham",
    category: "investigation",
    actors: ["andrew-do", "rhiannon-do", "cheri-pham", "peter-pham"],
  },
  {
    date: "Oct 22, 2024",
    sortKey: "2024-10-22",
    event: "Andrew Do pleads guilty to conspiracy to commit bribery; resigns",
    category: "legal",
    actors: ["andrew-do"],
  },
  {
    date: "Oct 23, 2024",
    sortKey: "2024-10-23",
    event:
      "Chris Wangsaporn resigns, the day after LAist published article about Josie Batres/$275K contract",
    category: "legal",
    actors: ["chris-wangsaporn"],
  },
  {
    date: "December 2024",
    sortKey: "2024-12-01",
    event:
      "Peter Pham flees to Taipei, Taiwan on one-way ticket. No extradition treaty between US and Taiwan.",
    category: "flight",
    actors: ["peter-pham"],
  },
  {
    date: "Jan 16, 2025",
    sortKey: "2025-01-16",
    event:
      "OC files First Amended Complaint against H2H in San Diego Superior Court (filed there due to Cheri Pham's judgeship in OC)",
    category: "legal",
    actors: [
      "thanh-huong-nguyen",
      "loc-nguyen",
      "michael-nguyen",
      "hand-to-hand",
    ],
  },
  {
    date: "June 2025",
    sortKey: "2025-06-01",
    event:
      "Federal indictment of Peter Pham (15 counts) and Thanh Huong Nguyen",
    category: "legal",
    actors: ["peter-pham", "thanh-huong-nguyen"],
  },
];

export const MONEY_FLOWS: MoneyFlow[] = [
  {
    from: "Orange County",
    to: "viet-america-society",
    amount: "$7.2M+",
    description:
      "CARES Act and ARPA COVID relief contracts authorized by Andrew Do",
  },
  {
    from: "Orange County",
    to: "hand-to-hand",
    amount: "$3M",
    description: "COVID relief contracts authorized by Andrew Do",
  },
  {
    from: "viet-america-society",
    to: "perfume-river",
    amount: "$100K–$315K/month",
    description: "Fake vendor payments; primary laundering channel",
  },
  {
    from: "viet-america-society",
    to: "peter-pham",
    amount: "Millions",
    description: "Personal checks directly to Pham",
  },
  {
    from: "viet-america-society",
    to: "josie-batres",
    amount: "$10K/month",
    description: "Fake consulting payments to Talentgate Inc.",
  },
  {
    from: "viet-america-society",
    to: "behavioral-health-solutions",
    amount: "$300K+",
    description: "Three $100K checks labeled 'Donation'",
  },
  {
    from: "viet-america-society",
    to: "hd-construction",
    amount: "Millions",
    description: "Fake construction vendor payments",
  },
  {
    from: "perfume-river",
    to: "rhiannon-do",
    amount: "$224K + $381.5K escrow",
    description:
      "$8K/month bribe payments over 2+ years; plus Tustin house purchase",
    legalCharge: "Bribery",
  },
  {
    from: "d-air-conditioning",
    to: "ilene-do",
    amount: "$75K",
    description: "Three $25,000 checks as bribe to Andrew Do's elder daughter",
    legalCharge: "Bribery",
  },
  {
    from: "peter-pham",
    to: "ilene-do",
    amount: "$25K",
    description: "One direct $25,000 check",
    legalCharge: "Bribery",
  },
  {
    from: "hand-to-hand",
    to: "perfume-river",
    amount: "$500K",
    description: "Day-one looting after county deposit",
    legalCharge: "Money laundering",
  },
  {
    from: "hand-to-hand",
    to: "hd-construction",
    amount: "$125K",
    description: "Check memo: 'Construction Restaurant'",
    legalCharge: "Money laundering Count Fourteen",
  },
  {
    from: "hand-to-hand",
    to: "d-air-conditioning",
    amount: "$50K",
    description: "Laundering payment",
  },
  {
    from: "hand-to-hand",
    to: "stmm-real-estate",
    amount: "$144K",
    description:
      "Two years of personal residential rent paid with COVID meal funds",
    legalCharge: "Money laundering",
  },
  {
    from: "hand-to-hand",
    to: "angel-nail-spa",
    amount: "$30K",
    description: "Thanh Huong Nguyen's nail salon; booked as 'meals provided'",
  },
  {
    from: "hand-to-hand",
    to: "michael-nguyen",
    amount: "Hundreds of thousands",
    description:
      "Structured ATM cash withdrawals of $9,500 each to evade IRS reporting",
    legalCharge: "Structuring",
  },
];

export const OUTSTANDING_QUESTIONS: OutstandingQuestion[] = [
  {
    id: "q1",
    question: "Who owns D Air Conditioning Co. LLC?",
    context:
      "Owner name not in any public filing reviewed. This person is an unindicted co-conspirator who accepted and redistributed over $256,000 in stolen federal funds — including issuing bribe checks directly to Ilene Do.",
    relatedActors: ["ilene-do", "peter-pham"],
  },
  {
    id: "q2",
    question:
      "What is the OCHCA housing program that the Anabel Garcia HIPAA form was feeding into?",
    context:
      "The May 24, 2023 OCHCA HIPAA authorization form — circulated at churches by a Huntington Beach social worker — authorized release of medical, mental health, and substance abuse records for a housing program at 405 W. 5th St, Santa Ana (OCHCA headquarters). H2H's stated mission included providing 'aide and food to disabled locals and homeless,' and its articles of incorporation cite housing-adjacent services. A housing program extension using the same church-based recruitment methodology would be a logical next phase of the scheme.",
    relatedActors: ["thanh-huong-nguyen"],
  },
  {
    id: "q3",
    question:
      "Is Anabel Garcia (HB Homeless Task Force social worker) acting independently or was she directed by someone in the network?",
    context:
      "Garcia was circulating OCHCA HIPAA forms at churches in the same Vietnamese Catholic community connected to VAS/H2H operators in May 2023 — exactly when both fraudulent contracts were active.",
  },
  {
    id: "q4",
    question: "Who is Truyen Van Nguyen?",
    context:
      "Received two $50,000 cashier's checks from Thanh Huong Nguyen (Feb 22, 2023) using stolen county funds. Not publicly identified or charged.",
    relatedActors: ["thanh-huong-nguyen"],
  },
  {
    id: "q5",
    question: "Who is Son Pham?",
    context:
      "Received $25,000 from H2H on January 10, 2023. Not publicly identified.",
    relatedActors: ["thanh-huong-nguyen"],
  },
  {
    id: "q6",
    question: "Who owns STMM Real Estate LLC?",
    context:
      "Received $144,000 in rent payments from county fraud funds (two years of Thanh Huong Nguyen's personal residence rent). Owner's connection to the network not public.",
    relatedActors: ["thanh-huong-nguyen"],
  },
  {
    id: "q7",
    question: "Will Peter Pham ever be extradited?",
    context:
      "The United States has no extradition treaty with Taiwan. Pham fled on a one-way ticket in December 2024 and remains at large. His 15-count federal indictment is outstanding.",
    relatedActors: ["peter-pham"],
  },
  {
    id: "q8",
    question:
      "Will Cheri Pham face judicial discipline from the Commission on Judicial Performance?",
    context:
      "Her home was raided by the FBI in August 2024, her husband pled guilty to federal bribery, and her daughters received hundreds of thousands of dollars in stolen COVID funds. No public announcement from CJP as of last reporting.",
    relatedActors: ["cheri-pham", "andrew-do"],
  },
  {
    id: "q9",
    question: "What is Brian Probolsky's specific connection to the HB nonprofit ecosystem?",
    context:
      "'Probolsky' appeared as a keyword in HB nonprofit OCR document scans — suggesting this name appeared in nonprofit or county documents connected to the broader patronage network surrounding Andrew Do.",
    relatedActors: ["brian-probolsky", "ilene-do"],
  },
];

export const STATUS_LABELS: Record<LegalStatus, string> = {
  convicted: "Convicted",
  indicted: "Indicted",
  fugitive: "Fugitive",
  civil_defendant: "Civil Defendant",
  unnamed_individual: "Unnamed in Indictment",
  not_charged: "Not Charged",
};

export const STATUS_COLORS: Record<LegalStatus, string> = {
  convicted: "bg-red-100 text-red-800 border-red-200",
  indicted: "bg-orange-100 text-orange-800 border-orange-200",
  fugitive: "bg-purple-100 text-purple-800 border-purple-200",
  civil_defendant: "bg-yellow-100 text-yellow-800 border-yellow-200",
  unnamed_individual: "bg-blue-100 text-blue-800 border-blue-200",
  not_charged: "bg-gray-100 text-gray-700 border-gray-200",
};

export const TIER_LABELS: Record<ActorTier, string> = {
  primary: "Primary Defendants",
  do_family: "Do Family",
  h2h_officers: "H2H Officers",
  government_enablers: "Government Enablers",
  church_layer: "Community Connections",
  unidentified: "Unidentified Actors",
};

export const CATEGORY_COLORS: Record<TimelineEvent["category"], string> = {
  contract: "bg-blue-500",
  crime: "bg-red-500",
  investigation: "bg-purple-500",
  legal: "bg-green-500",
  flight: "bg-orange-500",
  other: "bg-gray-400",
};
