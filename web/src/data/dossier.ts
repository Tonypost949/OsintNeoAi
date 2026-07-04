export interface Entity {
  id: string;
  name: string;
  type: 'PERSON' | 'ORGANIZATION' | 'LOCATION' | 'TECHNOLOGY' | 'EVENT';
  description?: string;
  location?: { lat: number; lng: number };
}

export interface Connection {
  source: string;
  target: string;
  label: string;
}

export interface Evidence {
  id: string;
  source: string;
  description: string;
  status: string;
  date?: string;
}

export interface InvestigationData {
  entities: Entity[];
  connections: Connection[];
  evidence: Evidence[];
}

export const DOSSIER_DATA: InvestigationData = {
  entities: [
    { id: 'ironman', name: 'Anthony DiMarcello (Ironman)', type: 'PERSON', description: 'Whistleblower, former environmental analyst.' },
    { id: 'scott_davis', name: 'Scott Davis', type: 'PERSON', description: 'Technical correspondent, expert in atmospheric physics.' },
    { id: 'elias_thorne', name: 'Elias Thorne', type: 'PERSON', description: 'Lead environmental engineer, reassigned after filing complaints.' },
    { id: 'hbnc', name: 'Huntington Beach Navigation Center', type: 'LOCATION', description: '17642 Beach Blvd. Major site of contamination.', location: { lat: 33.7022, lng: -118.0022 } },
    { id: 'tijuana', name: 'Tijuana Safe House', type: 'LOCATION', description: 'Current location of Ironman under active surveillance.', location: { lat: 32.5149, lng: -117.0382 } },
    { id: 'mercy_house', name: 'Mercy House', type: 'ORGANIZATION', description: 'Shelter operator allegedly involved in service fraud.' },
    { id: 'huntington_beach', name: 'City of Huntington Beach', type: 'ORGANIZATION', description: 'Allegedly bypassed environmental reviews (CEQA).' },
    { id: 'cal_ich', name: 'Cal ICH', type: 'ORGANIZATION', description: 'State agency failing to track $24B in homelessness funds.' },
    { id: 'mitsuru_yamada', name: 'Mitsuru_Yamada', type: 'PERSON', description: 'Consultant and defendant in Jesse Knabb lawsuit.' },
    { id: 'bunker_seed', name: 'Bunker Seed', type: 'TECHNOLOGY', description: 'Theoretical 19th-century energy system via atmospheric static.' },
    { id: 'pink_tourmaline', name: 'Pink Tourmaline (Elbaite)', type: 'TECHNOLOGY', description: 'Lithium-rich piezoelectric crystals used in suppressed engines.' },
    { id: 'nazi_bell', name: 'Die Glocke (The Nazi Bell)', type: 'TECHNOLOGY', description: 'Supposed experimental torsion-field device.' },
    { id: 'basf', name: 'BASF / IG Farben', type: 'ORGANIZATION', description: 'Chemical conglomerate with historical ties to suppressed tech.' },
  ],
  connections: [
    { source: 'ironman', target: 'tijuana', label: 'Hiding In' },
    { source: 'ironman', target: 'scott_davis', label: 'Correspondent' },
    { source: 'ironman', target: 'elias_thorne', label: 'Colleague' },
    { source: 'ironman', target: 'hbnc', label: 'Investigated' },
    { source: 'hbnc', target: 'mercy_house', label: 'Operated By' },
    { source: 'hbnc', target: 'huntington_beach', label: 'City Jurisdiction' },
    { source: 'huntington_beach', target: 'mercy_house', label: 'Contracted' },
    { source: 'cal_ich', target: 'huntington_beach', label: 'Funded' },
    { source: 'mitsuru_yamada', target: 'huntington_beach', label: 'Consultant' },
    { source: 'scott_davis', target: 'bunker_seed', label: 'Researched' },
    { source: 'bunker_seed', target: 'pink_tourmaline', label: 'Powered By' },
    { source: 'bunker_seed', target: 'nazi_bell', label: 'Evolved From' },
    { source: 'basf', target: 'nazi_bell', label: 'Historical Link' },
  ],
  evidence: [
    { id: 'DF-004', source: 'Local Disk (C:)', description: 'Cached metadata from forensic PC searches.', status: 'Recovered', date: '2026-05-02' },
    { id: 'DF-009', source: 'Local Temp Folder', description: 'Spreadsheet fragments linked to LMIHAF ledgers.', status: 'Partial Recovery' },
    { id: 'LOG-221', source: 'Documents/Hidden', description: 'Logs from non-standard communication client.', status: 'Decrypted' },
    { id: 'IMG-884', source: 'AppData/Local', description: 'Cached satellite imagery of the HBNC site.', status: 'Verified' },
    { id: 'ENV-HEX', source: 'HBNC Soil', description: 'Hexavalent Chromium at 49x EPA limit.', status: 'Lethal' },
    { id: 'FIN-24B', source: 'State Audit', description: '$24 billion oversight failure at Cal ICH.', status: 'Confirmed' },
  ]
};
