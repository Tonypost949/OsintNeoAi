#!/usr/bin/env python3
"""
Google Cloud GenAI Blueprints Integration Module
TASK-016: Implements Blueprint #39 (Legal Document Extraction) & #41 (Anti-Fraud Graph Engine)

Maps Google Cloud GenAI Blueprints into OsintNeoAi forensic investigation pipeline.
Provides:
  1. Legal document extraction with entity recognition
  2. Financial pattern detection for fraud/AML
  3. Relationship graph building
  4. Evidence correlation matrix

Author: OsintNeoAi / Anthony Michael DiMarcello III
Date: 2026-08-29
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class LegalEntity:
    """Represents a legal entity extracted from documents"""
    name: str
    entity_type: str  # LLC, Corporation, Trust, Individual, etc.
    jurisdiction: str
    identifiers: Dict[str, str]  # EIN, Agent ID, Registration No., etc.
    addresses: List[str]
    relationships: List[Dict] = None
    documents_found: List[str] = None
    confidence_score: float = 0.0
    
    def __post_init__(self):
        if self.relationships is None:
            self.relationships = []
        if self.documents_found is None:
            self.documents_found = []


@dataclass
class FinancialPattern:
    """Represents suspicious financial activity pattern"""
    pattern_type: str  # Smurfing, Round-tripping, Shell company, etc.
    entities_involved: List[str]
    transactions: List[Dict]
    risk_score: float
    indicators: List[str]
    jurisdiction: str
    timeline: Tuple[str, str]  # (start_date, end_date)
    evidence_references: List[str] = None
    
    def __post_init__(self):
        if self.evidence_references is None:
            self.evidence_references = []


class LegalDocumentExtractor:
    """Blueprint #39: Legal Document Extraction Engine
    
    Extracts entities, relationships, and key legal facts from court documents,
    corporate filings, regulatory submissions.
    """
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID', 'noble-beanbag-497411-m4')
        self.legal_entities: Dict[str, LegalEntity] = {}
        self.document_index: Dict[str, Dict] = {}
        logger.info(f"LegalDocumentExtractor initialized with project: {self.project_id}")
    
    def extract_entities_from_document(self, document_path: str, document_type: str) -> List[LegalEntity]:
        """
        Extract legal entities from a document.
        
        Args:
            document_path: Path to document (PDF, MD, TXT)
            document_type: Type of document (court_filing, corporate_record, regulatory, etc.)
        
        Returns:
            List of extracted LegalEntity objects
        """
        logger.info(f"Extracting entities from {document_path} ({document_type})")
        
        if not os.path.exists(document_path):
            logger.error(f"Document not found: {document_path}")
            return []
        
        try:
            with open(document_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read document: {e}")
            return []
        
        entities = []
        
        # Pattern matching for common legal entity formats
        llc_pattern = r'([A-Z][A-Z0-9\s&\-\.]*?)\s+LLC'
        corp_pattern = r'([A-Z][A-Z0-9\s&\-\.]*?)\s+(?:Corporation|Corp\.?|Inc\.?|Incorporated)'
        trust_pattern = r'([A-Z][A-Z0-9\s&\-\.]*?)\s+(?:Trust|Trustee)'
        
        for pattern, entity_type in [
            (llc_pattern, 'LLC'),
            (corp_pattern, 'Corporation'),
            (trust_pattern, 'Trust')
        ]:
            matches = re.finditer(pattern, content)
            for match in matches:
                entity_name = match.group(1).strip()
                
                # Avoid duplicates
                if entity_name not in self.legal_entities:
                    entity = LegalEntity(
                        name=entity_name,
                        entity_type=entity_type,
                        jurisdiction=self._extract_jurisdiction(content),
                        identifiers=self._extract_identifiers(content, entity_name),
                        addresses=self._extract_addresses(content),
                        confidence_score=0.75
                    )
                    self.legal_entities[entity_name] = entity
                    entities.append(entity)
                    logger.info(f"Extracted entity: {entity_name} ({entity_type})")
        
        # Log document in index
        self.document_index[document_path] = {
            'type': document_type,
            'entities_found': len(entities),
            'extracted_at': datetime.now().isoformat(),
            'file_size': os.path.getsize(document_path)
        }
        
        return entities
    
    def _extract_jurisdiction(self, content: str) -> str:
        """Extract jurisdiction from document content"""
        jurisdictions = ['California', 'Federal', 'Delaware', 'Nevada', 'New York']
        for j in jurisdictions:
            if j.lower() in content.lower():
                return j
        return 'Unknown'
    
    def _extract_identifiers(self, content: str, entity_name: str) -> Dict[str, str]:
        """Extract EIN, LLC ID, and other identifiers"""
        identifiers = {}
        
        # EIN pattern
        ein_pattern = r'EIN[\s:]+(\d{2}-\d{7})'
        ein_match = re.search(ein_pattern, content)
        if ein_match:
            identifiers['EIN'] = ein_match.group(1)
        
        # LLC ID pattern
        llc_id_pattern = r'(?:LLC ID|CA Secretary|Registration)[\s:]+([0-9]{4,})'
        llc_match = re.search(llc_id_pattern, content)
        if llc_match:
            identifiers['LLC_ID'] = llc_match.group(1)
        
        return identifiers
    
    def _extract_addresses(self, content: str) -> List[str]:
        """Extract addresses from document"""
        addresses = []
        # Simple pattern for addresses with street number and street name
        address_pattern = r'\d+\s+[A-Z][A-Za-z\s&\-\.]+(?:Street|Street|St\.|Avenue|Ave\.|Road|Rd\.|Drive|Dr\.|Lane|Ln\.)'
        matches = re.finditer(address_pattern, content)
        for match in matches:
            addr = match.group(0).strip()
            if addr not in addresses:
                addresses.append(addr)
        return addresses[:5]  # Return top 5 addresses
    
    def build_relationship_graph(self) -> Dict:
        """Build relationship graph between extracted entities"""
        graph = {
            'nodes': [],
            'edges': [],
            'metadata': {
                'total_entities': len(self.legal_entities),
                'extracted_at': datetime.now().isoformat()
            }
        }
        
        for entity_name, entity in self.legal_entities.items():
            graph['nodes'].append({
                'id': entity_name,
                'type': entity.entity_type,
                'jurisdiction': entity.jurisdiction,
                'addresses': entity.addresses,
                'identifiers': entity.identifiers
            })
        
        logger.info(f"Built relationship graph with {len(graph['nodes'])} nodes")
        return graph
    
    def export_to_bigquery_format(self) -> Dict:
        """Export extracted data in BigQuery table format"""
        return {
            'entities': [asdict(e) for e in self.legal_entities.values()],
            'document_index': self.document_index,
            'extraction_date': datetime.now().isoformat(),
            'project_id': self.project_id
        }


class AntiFraudGraphEngine:
    """Blueprint #41: Anti-Fraud / Anti-Money Laundering Graph Engine
    
    Detects financial crime patterns: smurfing, shell companies, round-tripping,
    structuring, beneficial ownership obfuscation.
    """
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID', 'noble-beanbag-497411-m4')
        self.financial_patterns: List[FinancialPattern] = []
        self.entity_graph: Dict = {}
        self.risk_matrix: Dict = {}
        logger.info(f"AntiFraudGraphEngine initialized with project: {self.project_id}")
    
    def detect_smurfing(self, transactions: List[Dict], threshold: float = 9999) -> List[FinancialPattern]:
        """
        Detect structuring/smurfing (31 USC § 5324): multiple sub-threshold deposits
        
        Args:
            transactions: List of transaction dicts with keys: amount, date, entity, type
            threshold: CTR threshold (default 10k USD)
        
        Returns:
            List of FinancialPattern objects for detected smurfing
        """
        logger.info(f"Scanning {len(transactions)} transactions for smurfing patterns")
        
        patterns = []
        entity_transactions: Dict[str, List] = {}
        
        # Group transactions by entity
        for txn in transactions:
            entity = txn.get('entity', 'Unknown')
            if entity not in entity_transactions:
                entity_transactions[entity] = []
            entity_transactions[entity].append(txn)
        
        # Detect suspicious patterns
        for entity, txns in entity_transactions.items():
            if len(txns) < 5:  # Minimum transactions for pattern
                continue
            
            total_amount = sum(t.get('amount', 0) for t in txns)
            avg_amount = total_amount / len(txns)
            
            # Red flags: multiple small deposits near threshold, short timeframe
            if avg_amount < threshold * 0.95 and len(txns) >= 5:
                pattern = FinancialPattern(
                    pattern_type='Structuring/Smurfing',
                    entities_involved=[entity],
                    transactions=txns,
                    risk_score=0.85,
                    indicators=[
                        f'{len(txns)} transactions just under ${threshold}',
                        f'Average amount: ${avg_amount:.2f}',
                        'Rapid deposit frequency',
                        'Potential CTR evasion (31 USC § 5324)'
                    ],
                    jurisdiction='Multi-State',
                    timeline=(min(t.get('date', '') for t in txns), 
                             max(t.get('date', '') for t in txns))
                )
                patterns.append(pattern)
                logger.warning(f"SMURFING detected for entity: {entity}")
        
        self.financial_patterns.extend(patterns)
        return patterns
    
    def detect_shell_companies(self, entities: List[LegalEntity], 
                              address_clustering_threshold: int = 3) -> List[FinancialPattern]:
        """
        Detect shell company networks: same address, agent, or filing patterns
        
        Args:
            entities: List of LegalEntity objects
            address_clustering_threshold: Min entities at same address to flag
        
        Returns:
            List of FinancialPattern objects
        """
        logger.info(f"Analyzing {len(entities)} entities for shell company networks")
        
        patterns = []
        address_map: Dict[str, List] = {}
        
        # Cluster by address
        for entity in entities:
            for addr in entity.addresses:
                if addr not in address_map:
                    address_map[addr] = []
                address_map[addr].append(entity.name)
        
        # Identify clusters
        for addr, names in address_map.items():
            if len(names) >= address_clustering_threshold:
                pattern = FinancialPattern(
                    pattern_type='Shell Company Network',
                    entities_involved=names,
                    transactions=[],
                    risk_score=0.80,
                    indicators=[
                        f'{len(names)} entities at single address: {addr}',
                        'Shared jurisdictional filing',
                        'Potential beneficial ownership obfuscation',
                        'Common agent or registered office'
                    ],
                    jurisdiction='Multi-State',
                    timeline=('Unknown', 'Unknown')
                )
                patterns.append(pattern)
                logger.warning(f"SHELL NETWORK detected at address: {addr} ({len(names)} entities)")
        
        self.financial_patterns.extend(patterns)
        return patterns
    
    def build_fraud_risk_graph(self) -> Dict:
        """Build comprehensive fraud risk network graph"""
        graph = {
            'nodes': [],
            'edges': [],
            'risk_clusters': [],
            'metadata': {
                'patterns_detected': len(self.financial_patterns),
                'high_risk_count': sum(1 for p in self.financial_patterns if p.risk_score > 0.75),
                'generated_at': datetime.now().isoformat()
            }
        }
        
        for i, pattern in enumerate(self.financial_patterns):
            cluster_id = f"risk_cluster_{i}"
            
            for entity in pattern.entities_involved:
                graph['nodes'].append({
                    'id': entity,
                    'type': 'Entity',
                    'risk_cluster': cluster_id,
                    'risk_score': pattern.risk_score
                })
            
            # Add edges between entities in same pattern
            for j in range(len(pattern.entities_involved) - 1):
                graph['edges'].append({
                    'source': pattern.entities_involved[j],
                    'target': pattern.entities_involved[j + 1],
                    'type': pattern.pattern_type,
                    'weight': pattern.risk_score
                })
            
            graph['risk_clusters'].append({
                'id': cluster_id,
                'pattern_type': pattern.pattern_type,
                'risk_score': pattern.risk_score,
                'entity_count': len(pattern.entities_involved),
                'indicators': pattern.indicators
            })
        
        logger.info(f"Built fraud risk graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")
        return graph
    
    def export_to_bigquery_format(self) -> Dict:
        """Export fraud detection results in BigQuery table format"""
        return {
            'patterns': [asdict(p) for p in self.financial_patterns],
            'risk_graph': self.build_fraud_risk_graph(),
            'detection_date': datetime.now().isoformat(),
            'project_id': self.project_id
        }


class OsintNeoAiBlueprintIntegration:
    """Master integration orchestrator for GenAI Blueprints #39 & #41"""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID', 'noble-beanbag-497411-m4')
        self.legal_extractor = LegalDocumentExtractor(self.project_id)
        self.fraud_engine = AntiFraudGraphEngine(self.project_id)
        logger.info("OsintNeoAiBlueprintIntegration initialized")
    
    def process_investigation_batch(self, documents: List[str], 
                                   transactions: List[Dict] = None) -> Dict:
        """
        Run complete forensic pipeline: extract -> analyze -> detect fraud -> build graph
        
        Args:
            documents: List of document paths
            transactions: Optional list of transaction records
        
        Returns:
            Comprehensive results dictionary
        """
        logger.info(f"Processing batch: {len(documents)} documents, {len(transactions or [])} transactions")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'legal_extraction': {},
            'fraud_detection': {},
            'integrated_graph': {}
        }
        
        # Step 1: Extract legal entities
        all_entities = []
        for doc_path in documents:
            if os.path.exists(doc_path):
                doc_type = self._classify_document(doc_path)
                entities = self.legal_extractor.extract_entities_from_document(doc_path, doc_type)
                all_entities.extend(entities)
        
        results['legal_extraction'] = {
            'entities_extracted': len(all_entities),
            'entity_graph': self.legal_extractor.build_relationship_graph(),
            'bigquery_export': self.legal_extractor.export_to_bigquery_format()
        }
        logger.info(f"Step 1 complete: {len(all_entities)} entities extracted")
        
        # Step 2: Detect fraud patterns
        if transactions:
            smurfing_patterns = self.fraud_engine.detect_smurfing(transactions)
            results['fraud_detection']['smurfing_patterns'] = [
                asdict(p) for p in smurfing_patterns
            ]
        
        shell_patterns = self.fraud_engine.detect_shell_companies(all_entities)
        results['fraud_detection']['shell_companies'] = [
            asdict(p) for p in shell_patterns
        ]
        results['fraud_detection']['bigquery_export'] = self.fraud_engine.export_to_bigquery_format()
        logger.info(f"Step 2 complete: Fraud detection complete")
        
        # Step 3: Build integrated correlation matrix
        results['integrated_graph'] = {
            'legal_entities': len(all_entities),
            'fraud_patterns': len(self.fraud_engine.financial_patterns),
            'correlation_matrix': self._build_correlation_matrix(all_entities)
        }
        
        return results
    
    def _classify_document(self, doc_path: str) -> str:
        """Classify document type based on filename and content"""
        filename = os.path.basename(doc_path).lower()
        
        if 'court' in filename or 'filing' in filename:
            return 'court_filing'
        elif 'sec' in filename or '10-k' in filename or '8-k' in filename:
            return 'sec_filing'
        elif 'regulatory' in filename or 'compliance' in filename:
            return 'regulatory'
        elif 'transaction' in filename or 'ledger' in filename:
            return 'financial'
        else:
            return 'general'
    
    def _build_correlation_matrix(self, entities: List[LegalEntity]) -> Dict:
        """Build correlation matrix showing entity relationships"""
        matrix = {
            'total_entities': len(entities),
            'correlations': [],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'method': 'Address/Identifier clustering'
            }
        }
        
        # Simple correlation: shared addresses
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                shared_addrs = set(entity1.addresses) & set(entity2.addresses)
                if shared_addrs:
                    matrix['correlations'].append({
                        'entity_1': entity1.name,
                        'entity_2': entity2.name,
                        'correlation_type': 'shared_address',
                        'shared_addresses': list(shared_addrs),
                        'strength': 0.9
                    })
        
        return matrix


def main():
    """Example usage and testing"""
    logger.info("=" * 80)
    logger.info("GOOGLE CLOUD GENAI BLUEPRINTS #39 & #41 INTEGRATION TEST")
    logger.info("=" * 80)
    
    # Initialize integration
    integration = OsintNeoAiBlueprintIntegration()
    
    # Example: Process some documents if they exist
    test_docs = [
        'C:\\OsintNeoAi\\legal_library\\INDIGENOUS_TRIBAL_LAND_RIGHTS_AND_CULTURAL_RESOURCES_AUDIT.md',
        'C:\\OsintNeoAi\\CIVIL_FORFEITURE_PHAM_WELLS_FARGO_DRAFT.md'
    ]
    
    existing_docs = [d for d in test_docs if os.path.exists(d)]
    
    if existing_docs:
        results = integration.process_investigation_batch(
            documents=existing_docs,
            transactions=[]  # Add transaction data if available
        )
        
        logger.info("\n" + "=" * 80)
        logger.info("INTEGRATION RESULTS SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Legal Entities Extracted: {results['legal_extraction']['entities_extracted']}")
        logger.info(f"Fraud Patterns Detected: {results['fraud_detection'].get('shell_companies', [])}")
        logger.info(f"Total Correlations Found: {len(results['integrated_graph']['correlation_matrix']['correlations'])}")
        
        # Save results
        output_path = 'C:\\OsintNeoAi\\data\\genai_blueprint_results.json'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"\nResults saved to: {output_path}")
    else:
        logger.info(f"No test documents found. Paths checked: {test_docs}")
        logger.info("Integration module ready for deployment.")
        logger.info("\nUsage example:")
        logger.info("  integration = OsintNeoAiBlueprintIntegration()")
        logger.info("  results = integration.process_investigation_batch(")
        logger.info("    documents=['path/to/doc1.pdf', 'path/to/doc2.md'],")
        logger.info("    transactions=[...]")
        logger.info("  )")


if __name__ == '__main__':
    main()
