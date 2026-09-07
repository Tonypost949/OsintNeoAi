"""
OsintNeoAi — Featured Story #1 Loader
Seeds the builder master workspace as Featured Story #1.

Usage:
  python agent/featured_story_loader.py --seed    # Seed builder workspace from repo evidence
  python agent/featured_story_loader.py --status  # Check seeding status

Evidence sources:
  briefings/*.md            Whistleblower briefings
  evidence/                 EDR environmental reports (PDF)
  autonomous_taxfunded_ledger.json  FOIA records
  newspaper_stories.json    Existing story DB
  crypto_ledger_tracker.json        Token metrics
"""

import os
import sys
import uuid
import json
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
GCP_PROJECT = os.environ.get("GCP_PROJECT", "noble-beanbag-497411-m4")
BQ_DATASET  = os.environ.get("BQ_WORKSPACE_DATASET", "platform")

W_TABLE = "{}.{}.workspaces".format(GCP_PROJECT, BQ_DATASET)
S_TABLE = "{}.{}.newspaper_stories".format(GCP_PROJECT, BQ_DATASET)

BUILDER_WORKSPACE_ID   = "builder-master-featured-001"
BUILDER_WALLET         = os.environ.get("BUILDER_WALLET", "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
BUILDER_DISPLAY_NAME   = "OsintNeoAi — Builder Master Investigation"
BUILDER_EMAIL          = "amd949609@gmail.com"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load_briefings():
    results = []
    d = REPO_ROOT / "briefings"
    if not d.exists():
        logger.warning("briefings/ not found")
        return results
    for f in d.glob("*.md"):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
            lines = text.strip().splitlines()
            title = lines[0].lstrip("# ").strip() if lines else f.stem
            summary = " ".join(lines[1:4]).strip()[:400]
            results.append({"file": f.name, "title": title, "summary": summary, "body": text[:8000], "tags": ["whistleblower", "forensic", "briefing"], "evidence_refs": ["briefings/{}".format(f.name)]})
            logger.info("  Briefing: %s", f.name)
        except Exception as e:
            logger.warning("  Could not load %s: %s", f.name, e)
    return results


def _edr_summary():
    count = sum(1 for _ in (REPO_ROOT / "evidence").rglob("*.pdf")) if (REPO_ROOT / "evidence").exists() else 0
    return count


def _load_foia():
    records = []
    for path in [REPO_ROOT / "autonomous_taxfunded_ledger.json", REPO_ROOT / "newspaper_stories.json"]:
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if isinstance(data, list):
                    records.extend(data[:3])
                elif isinstance(data, dict):
                    records.append(data)
            except Exception as e:
                logger.warning("  FOIA load warning %s: %s", path.name, e)
    return records


def _load_crypto():
    p = REPO_ROOT / "crypto_ledger_tracker.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return {}


def _build_body(briefings, edr_count, foia_records, crypto):
    lines = [
        "# OsintNeoAi — Master Investigation Dossier",
        "",
        "## Platform Overview",
        "OsintNeoAi exposes municipal corruption, environmental cover-ups, and financial fraud "
        "through OSINT, BigQuery graph analysis, and direct regulatory submission.",
        "",
        "## Evidence Summary",
        "- **EDR Environmental Reports:** {} PDF documents".format(edr_count),
        "- **Whistleblower Briefings:** {} active case dossiers".format(len(briefings)),
        "- **FOIA/Ledger Records:** {} filed records".format(len(foia_records)),
        "",
        "## Active Cases",
    ]
    for b in briefings[:6]:
        lines += ["### {}".format(b["title"]), b["summary"], ""]
    if foia_records:
        lines.append("## FOIA & Ledger Records")
        for rec in foia_records[:2]:
            if isinstance(rec, dict):
                for k, v in list(rec.items())[:3]:
                    lines.append("- **{}:** {}".format(k, v))
        lines.append("")
    lines += [
        "## Dual-Token Crypto Ecosystem",
        "- **TFT Token:** 14,200,000 supply — TaxFunded governance token",
        "- **OSINT Token:** 50,000,000 supply — Platform utility token",
        "- **DualAuditTokenBridge:** 12.5% APY, 1.05x growth multiplier",
        "- Token value grows with platform activity: workspaces, stories, FOIA submissions",
        "",
        "## Evidence Repository",
        "All evidence: https://github.com/Tonypost949/OsintNeoAi",
        "",
        "---",
        "_Featured Story #1 — OsintNeoAi Builder Master Workspace_",
    ]
    return "\n".join(lines)


def seed(bq_client):
    logger.info("=== Seeding Builder Master Workspace ===")
    now = _now_iso()
    ws_row = {
        "workspace_id":    BUILDER_WORKSPACE_ID,
        "user_id":         BUILDER_WORKSPACE_ID,
        "wallet_address":  BUILDER_WALLET,
        "author_identity": BUILDER_WALLET,
        "display_name":    BUILDER_DISPLAY_NAME,
        "email":           BUILDER_EMAIL,
        "is_public":       True,
        "is_featured":     True,
        "featured_rank":   1,
        "created_at":      now,
        "updated_at":      now,
        "tool_count":      0,
        "story_count":     0,
        "plan":            "builder",
    }
    errs = bq_client.insert_rows_json(W_TABLE, [ws_row])
    if errs:
        logger.error("Workspace insert error: %s", errs)
        return False
    logger.info("  Workspace created: %s", BUILDER_WORKSPACE_ID)

    briefings = _load_briefings()
    edr_count = _edr_summary()
    foia_records = _load_foia()
    crypto = _load_crypto()

    story_ids = []
    for b in briefings:
        sid = str(uuid.uuid4())
        errs = bq_client.insert_rows_json(S_TABLE, [{
            "story_id":        sid,
            "workspace_id":    BUILDER_WORKSPACE_ID,
            "author_identity": BUILDER_WALLET,
            "title":           b["title"],
            "summary":         b["summary"],
            "body":            b["body"],
            "tags":            b["tags"],
            "is_public":       True,
            "published_at":    now,
            "view_count":      0,
            "evidence_refs":   b["evidence_refs"],
        }])
        if not errs:
            story_ids.append(sid)
            logger.info("  Story published: %s", b["title"][:60])

    master_id = str(uuid.uuid4())
    master_body = _build_body(briefings, edr_count, foia_records, crypto)
    errs = bq_client.insert_rows_json(S_TABLE, [{
        "story_id":        master_id,
        "workspace_id":    BUILDER_WORKSPACE_ID,
        "author_identity": BUILDER_WALLET,
        "title":           "OsintNeoAi Master Dossier — Featured Investigation #1",
        "summary":         "HBNC contamination, Hexavalent Chromium cover-up, municipal RICO, federal non-response, TaxFunded dual-token crypto audit ledger.",
        "body":            master_body,
        "tags":            ["featured", "osint", "forensic", "rico", "foia", "crypto", "taxfunded", "hbnc"],
        "is_public":       True,
        "published_at":    now,
        "view_count":      0,
        "evidence_refs":   ["briefings/{}".format(b["file"]) for b in briefings],
    }])
    if errs:
        logger.error("Master story insert error: %s", errs)

    try:
        bq_client.query("UPDATE `{}` SET story_count = {} WHERE workspace_id = '{}'".format(W_TABLE, len(story_ids) + 1, BUILDER_WORKSPACE_ID)).result()
    except Exception as e:
        logger.warning("story_count update: %s", e)

    logger.info("=== Done: %d stories published. Featured Story #1 ID: %s ===", len(story_ids) + 1, master_id)
    return True


def status(bq_client):
    try:
        rows = list(bq_client.query("SELECT workspace_id, story_count, is_featured, plan FROM `{}` WHERE workspace_id = '{}' LIMIT 1".format(W_TABLE, BUILDER_WORKSPACE_ID)).result())
        if rows:
            logger.info("Builder workspace: %s", dict(rows[0]))
        else:
            logger.info("Not seeded yet. Run with --seed")
    except Exception as e:
        logger.error("Status check failed: %s", e)


def main():
    parser = argparse.ArgumentParser(description="Featured Story #1 Loader")
    parser.add_argument("--seed", action="store_true", help="Seed builder workspace")
    parser.add_argument("--status", action="store_true", help="Check seeding status")
    args = parser.parse_args()

    try:
        from google.cloud import bigquery
        bq_client = bigquery.Client(project=GCP_PROJECT)
    except ImportError:
        logger.error("google-cloud-bigquery not installed. Run: pip install google-cloud-bigquery")
        sys.exit(1)

    if args.seed:
        ok = seed(bq_client)
        sys.exit(0 if ok else 1)
    elif args.status:
        status(bq_client)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
