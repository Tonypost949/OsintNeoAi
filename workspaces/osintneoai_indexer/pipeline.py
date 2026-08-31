"""
OsintNeoAi Indexer: Unified End-to-End Execution Pipeline & CLI Entrypoint
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\pipeline.py
Milestone: M3 (Entity Resolution & Vault Storage) — Integration & Pipeline Orchestration

Connects:
LocalCrawler / GDriveStreamer -> DocumentExtractor -> Normalizers -> EntityResolver -> VaultDB -> CatalogExporter

Produces:
- SQLite 3NF Database: timeline_vault.db
- RFC 8785 Master JSON Catalog: master_timeline_catalog.json
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from config import (
    DEFAULT_DOWNLOADS_DIR,
    DEFAULT_EVIDENCE_DIR,
    DEFAULT_MASTER_CATALOG_PATH,
    DEFAULT_VAULT_DB_PATH,
    DEFAULT_WORKSPACE_DIR,
    IndexerConfig,
)
from connectors.gdrive_streamer import GDriveStreamer
from connectors.local_crawler import IngestedArtifact, LocalCrawler
from extractors.document_extractor import DocumentExtractor, ExtractedRecord
from resolution.entity_resolver import EntityResolver
from storage.catalog_exporter import CatalogExporter
from storage.vault_db import VaultDB

logger = logging.getLogger("osintneoai.pipeline")


# ============================================================================
# 1. PIPELINE TELEMETRY & RESULT CONTAINER
# ============================================================================

@dataclass
class PipelineResult:
    """
    Comprehensive execution telemetry returned after pipeline completion.
    """
    total_ingested_files: int = 0
    total_extracted_records: int = 0
    total_entities: int = 0
    total_mentions: int = 0
    total_events: int = 0
    total_transactions: int = 0
    total_relationships: int = 0
    vault_db_path: Optional[Path] = None
    master_catalog_path: Optional[Path] = None
    root_merkle_sha256: str = ""
    all_invariants_passed: bool = False
    elapsed_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)


# ============================================================================
# 2. UNIFIED PIPELINE ORCHESTRATOR
# ============================================================================

class OsintNeoAiIndexerPipeline:
    """
    High-throughput, streaming end-to-end indexer and timeline reconciliation pipeline.
    """

    def __init__(
        self,
        config: Optional[IndexerConfig] = None,
        vault_db_path: Optional[Union[str, Path]] = None,
        master_catalog_path: Optional[Union[str, Path]] = None,
        similarity_threshold: float = 0.88,
        integrity_mode: str = "development",
    ) -> None:
        self.config = config or IndexerConfig()
        self.vault_db_path = Path(vault_db_path) if vault_db_path else self.config.vault_db_path
        self.master_catalog_path = Path(master_catalog_path) if master_catalog_path else self.config.master_catalog_path
        self.similarity_threshold = similarity_threshold
        self.integrity_mode = integrity_mode

        # Initialize sub-systems
        self.crawler = LocalCrawler(
            target_paths=[self.config.evidence_dir, self.config.downloads_dir],
            chunk_size=self.config.chunk_size,
        )
        self.gdrive_streamer = GDriveStreamer(
            spool_dir=self.config.spool_dir,
        )
        self.extractor = DocumentExtractor()
        self.resolver = EntityResolver(similarity_threshold=self.similarity_threshold)
        self.vault_db = VaultDB(db_path=self.vault_db_path)
        self.catalog_exporter = CatalogExporter(vault_db=self.vault_db, output_path=self.master_catalog_path)

    def run(
        self,
        source_dirs: Optional[Sequence[Union[str, Path]]] = None,
        gdrive_urls: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
    ) -> PipelineResult:
        """
        Executes the full pipeline across target local directories and Google Drive sources.
        """
        start_time = time.time()
        result = PipelineResult(
            vault_db_path=self.vault_db_path,
            master_catalog_path=self.master_catalog_path,
        )

        logger.info("Starting OsintNeoAi Indexer Pipeline run...")

        # 1. Determine local search directories
        dirs_to_crawl: List[Path] = []
        if source_dirs:
            for d in source_dirs:
                p = Path(d)
                if p.exists():
                    dirs_to_crawl.append(p)
                else:
                    logger.warning("Source directory does not exist: %s", p)
        else:
            for default_dir in [self.config.evidence_dir, self.config.downloads_dir]:
                if default_dir.exists():
                    dirs_to_crawl.append(default_dir)

        # 2. Collect artifacts from LocalCrawler
        all_artifacts: List[IngestedArtifact] = []
        for crawl_dir in dirs_to_crawl:
            try:
                for art in self.crawler.crawl_directory(crawl_dir):
                    all_artifacts.append(art)
                    if limit and len(all_artifacts) >= limit:
                        break
            except Exception as e:
                err_msg = f"Error crawling {crawl_dir}: {e}"
                logger.error(err_msg)
                result.errors.append(err_msg)

            if limit and len(all_artifacts) >= limit:
                break

        # 3. Collect artifacts from Google Drive URLs
        if gdrive_urls:
            for url in gdrive_urls:
                try:
                    art = self.gdrive_streamer.resolve_url(url)
                    all_artifacts.append(art)
                    if limit and len(all_artifacts) >= limit:
                        break
                except Exception as e:
                    err_msg = f"Error downloading Google Drive link {url}: {e}"
                    logger.error(err_msg)
                    result.errors.append(err_msg)

                if limit and len(all_artifacts) >= limit:
                    break

        result.total_ingested_files = len(all_artifacts)
        logger.info("Ingested %d raw artifacts for processing.", result.total_ingested_files)

        # 4. Extract and normalize documents
        extracted_records: List[ExtractedRecord] = []
        for art in all_artifacts:
            try:
                rec = self.extractor.extract(art)
                extracted_records.append(rec)
            except Exception as e:
                err_msg = f"Error extracting artifact {art.source_uri}: {e}"
                logger.error(err_msg)
                result.errors.append(err_msg)

        result.total_extracted_records = len(extracted_records)
        logger.info("Extracted %d document records.", result.total_extracted_records)

        # 5. Execute Entity Resolution, Timeline Extraction & Graph Synthesis
        try:
            entities, mentions, events, transactions, relationships = self.resolver.extract_and_resolve(extracted_records)
            result.total_entities = len(entities)
            result.total_mentions = len(mentions)
            result.total_events = len(events)
            result.total_transactions = len(transactions)
            result.total_relationships = len(relationships)
            logger.info(
                "Resolved %d entities (%d mentions), %d events, %d transactions, %d relationships.",
                result.total_entities, result.total_mentions, result.total_events,
                result.total_transactions, result.total_relationships,
            )
        except Exception as e:
            err_msg = f"Error during entity resolution & graph synthesis: {e}"
            logger.error(err_msg)
            result.errors.append(err_msg)
            entities, mentions, events, transactions, relationships = [], [], [], [], []

        # 6. Store in SQLite Vault
        try:
            # Batch insert documents
            doc_rows = []
            for rec in extracted_records:
                doc_rows.append({
                    "document_id": rec.record_id,
                    "source_uri": rec.source_path,
                    "file_name": Path(rec.source_path).name,
                    "file_path": rec.source_path,
                    "file_size_bytes": rec.metadata.get("file_size_bytes", len(rec.extracted_text)),
                    "mime_type": rec.mime_type,
                    "file_sha256": rec.artifact_sha256,
                    "content_sha256": rec.artifact_sha256,
                    "ingestion_timestamp": rec.metadata.get("ingestion_timestamp", "2026-08-29T18:00:00Z"),
                    "document_date": rec.normalized_date,
                    "page_count": rec.metadata.get("page_count", 1),
                    "extracted_text": rec.extracted_text,
                    "ocr_confidence": rec.metadata.get("ocr_confidence", 1.0),
                    "raw_metadata_json": rec.metadata,
                })
            self.vault_db.insert_documents_batch(doc_rows)

            # Batch insert entities, mentions, events, transactions, relationships
            self.vault_db.insert_entities_batch(entities)
            self.vault_db.insert_mentions_batch(mentions)
            self.vault_db.insert_events_batch(events)
            self.vault_db.insert_financial_transactions_batch(transactions)
            self.vault_db.insert_relationships_batch(relationships)

            logger.info("Successfully committed all records to SQLite Vault: %s", self.vault_db_path)
        except Exception as e:
            err_msg = f"Error storing records in VaultDB: {e}"
            logger.error(err_msg)
            result.errors.append(err_msg)

        # 7. Export Master JSON Catalog & Compute Merkle Root
        try:
            catalog_path = self.catalog_exporter.export_to_file(
                output_path=self.master_catalog_path,
                integrity_mode=self.integrity_mode,
            )
            result.master_catalog_path = catalog_path

            # Load catalog to extract root hash and invariant status
            catalog_obj = self.catalog_exporter.build_catalog(integrity_mode=self.integrity_mode)
            result.root_merkle_sha256 = catalog_obj["catalog_metadata"]["root_merkle_sha256"]
            result.all_invariants_passed = catalog_obj["audit_invariants"]["all_invariants_passed"]

            logger.info("Successfully exported Master JSON Catalog: %s (Root: %s)", catalog_path, result.root_merkle_sha256)
        except Exception as e:
            err_msg = f"Error exporting Master JSON Catalog: {e}"
            logger.error(err_msg)
            result.errors.append(err_msg)

        result.elapsed_seconds = round(time.time() - start_time, 3)
        logger.info(
            "Pipeline completed in %.2fs. Invariants passed: %s",
            result.elapsed_seconds, result.all_invariants_passed
        )

        return result

    def process_records(self, records: Sequence[ExtractedRecord]) -> PipelineResult:
        """
        Directly processes pre-extracted document records without crawling/OCR.
        Useful for unit tests and direct ingestion streams.
        """
        start_time = time.time()
        result = PipelineResult(
            total_ingested_files=len(records),
            total_extracted_records=len(records),
            vault_db_path=self.vault_db_path,
            master_catalog_path=self.master_catalog_path,
        )

        entities, mentions, events, transactions, relationships = self.resolver.extract_and_resolve(records)
        result.total_entities = len(entities)
        result.total_mentions = len(mentions)
        result.total_events = len(events)
        result.total_transactions = len(transactions)
        result.total_relationships = len(relationships)

        doc_rows = []
        for rec in records:
            doc_rows.append({
                "document_id": rec.record_id,
                "source_uri": rec.source_path,
                "file_name": Path(rec.source_path).name,
                "file_path": rec.source_path,
                "file_size_bytes": rec.metadata.get("file_size_bytes", len(rec.extracted_text)),
                "mime_type": rec.mime_type,
                "file_sha256": rec.artifact_sha256,
                "content_sha256": rec.artifact_sha256,
                "ingestion_timestamp": rec.metadata.get("ingestion_timestamp", "2026-08-29T18:00:00Z"),
                "document_date": rec.normalized_date,
                "page_count": rec.metadata.get("page_count", 1),
                "extracted_text": rec.extracted_text,
                "ocr_confidence": rec.metadata.get("ocr_confidence", 1.0),
                "raw_metadata_json": rec.metadata,
            })
        self.vault_db.insert_documents_batch(doc_rows)
        self.vault_db.insert_entities_batch(entities)
        self.vault_db.insert_mentions_batch(mentions)
        self.vault_db.insert_events_batch(events)
        self.vault_db.insert_financial_transactions_batch(transactions)
        self.vault_db.insert_relationships_batch(relationships)

        self.catalog_exporter.export_to_file(output_path=self.master_catalog_path, integrity_mode=self.integrity_mode)
        catalog_obj = self.catalog_exporter.build_catalog(integrity_mode=self.integrity_mode)
        result.root_merkle_sha256 = catalog_obj["catalog_metadata"]["root_merkle_sha256"]
        result.all_invariants_passed = catalog_obj["audit_invariants"]["all_invariants_passed"]
        result.elapsed_seconds = round(time.time() - start_time, 3)

        return result


# ============================================================================
# 3. CLI ENTRYPOINT
# ============================================================================

def build_cli_parser() -> argparse.ArgumentParser:
    """Builds CLI argument parser for the indexer pipeline."""
    parser = argparse.ArgumentParser(
        description="OsintNeoAi Indexer: Document Extraction, Entity Resolution & Timeline Reconciliation Pipeline"
    )
    parser.add_argument(
        "--source-dir", "-s",
        action="append",
        dest="source_dirs",
        help="Source directory containing documents to crawl and index (can be specified multiple times)"
    )
    parser.add_argument(
        "--gdrive-url", "-g",
        action="append",
        dest="gdrive_urls",
        help="Google Drive public or shared link to download and index"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Maximum number of files to process"
    )
    parser.add_argument(
        "--vault-db",
        type=Path,
        default=DEFAULT_VAULT_DB_PATH,
        help="Output path for timeline_vault.db"
    )
    parser.add_argument(
        "--catalog-json",
        type=Path,
        default=DEFAULT_MASTER_CATALOG_PATH,
        help="Output path for master_timeline_catalog.json"
    )
    parser.add_argument(
        "--integrity-mode",
        choices=["development", "production", "forensic_court_ready"],
        default="development",
        help="Cryptographic and audit integrity mode"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.88,
        help="Entity resolution Jaro-Winkler fuzzy matching threshold"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose DEBUG logging"
    )
    return parser


def main() -> int:
    """Main CLI entrypoint function."""
    parser = build_cli_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    pipeline = OsintNeoAiIndexerPipeline(
        vault_db_path=args.vault_db,
        master_catalog_path=args.catalog_json,
        similarity_threshold=args.threshold,
        integrity_mode=args.integrity_mode,
    )

    result = pipeline.run(
        source_dirs=args.source_dirs,
        gdrive_urls=args.gdrive_urls,
        limit=args.limit,
    )

    print("\n" + "=" * 60)
    print("OSINTNEOAI INDEXER PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Total Ingested Files:       {result.total_ingested_files}")
    print(f"Total Extracted Records:    {result.total_extracted_records}")
    print(f"Canonical Entities:         {result.total_entities}")
    print(f"Entity Mentions:            {result.total_mentions}")
    print(f"Timeline Events:            {result.total_events}")
    print(f"Financial Transactions:     {result.total_transactions}")
    print(f"Relational Graph Edges:     {result.total_relationships}")
    print(f"Vault SQLite Database:      {result.vault_db_path}")
    print(f"Master JSON Catalog:        {result.master_catalog_path}")
    print(f"Root Merkle SHA-256:        {result.root_merkle_sha256}")
    print(f"Invariants Passed:          {result.all_invariants_passed}")
    print(f"Elapsed Time:               {result.elapsed_seconds:.3f}s")
    print("=" * 60)

    if result.errors:
        print(f"Errors encountered ({len(result.errors)}):")
        for err in result.errors[:10]:
            print(f"  - {err}")

    return 0 if result.all_invariants_passed else 1


if __name__ == "__main__":
    sys.exit(main())
