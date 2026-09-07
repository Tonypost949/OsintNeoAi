"""
OsintNeoAi — Multi-User Workspace API
workspace_id = user_id = wallet_address = author_identity (unified identity)

Routes:
  POST /api/workspaces/create           Create new user workspace
  GET  /api/workspaces/<id>             Get workspace metadata
  GET  /api/workspaces/public           List all public workspaces (featured first)
  POST /api/tools/import                Import GitHub repo as tool into workspace
  GET  /api/tools/status/<tool_id>      Check tool import status
  GET  /api/crypto/public               Public crypto dashboard (no login required)
  GET  /api/crypto/public/ledger-growth Token growth index tied to platform activity
  GET  /api/newspaper/featured          Featured Story #1 (builder workspace)
  POST /api/newspaper/publish           Publish investigation as newspaper story
  GET  /api/workspaces/<id>/stories     Get all public stories for a workspace
"""

import os
import uuid
import hashlib
import json
import logging
import threading
import subprocess
import tempfile
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, abort

logger = logging.getLogger(__name__)

workspace_bp = Blueprint("workspace", __name__, url_prefix="/api")

GCP_PROJECT = os.environ.get("GCP_PROJECT", "noble-beanbag-497411-m4")
BQ_DATASET  = os.environ.get("BQ_WORKSPACE_DATASET", "platform")
BUILDER_WORKSPACE_ID = "builder-master-featured-001"
BUILDER_WALLET = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

_bq_client = None

def _bq():
    global _bq_client
    if _bq_client is None:
        from google.cloud import bigquery
        _bq_client = bigquery.Client(project=GCP_PROJECT)
    return _bq_client

def _bq_param(name, value):
    from google.cloud import bigquery
    return bigquery.ScalarQueryParameter(name, "STRING", value)

def _run_query(sql, params=None):
    from google.cloud import bigquery
    job_config = bigquery.QueryJobConfig(query_parameters=params or [])
    try:
        rows = _bq().query(sql, job_config=job_config).result()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error("BQ query failed: %s", e)
        return []

W_TABLE = "{}.{}.workspaces".format(GCP_PROJECT, BQ_DATASET)
S_TABLE = "{}.{}.newspaper_stories".format(GCP_PROJECT, BQ_DATASET)
T_TABLE = "{}.{}.workspace_tools".format(GCP_PROJECT, BQ_DATASET)

_tables_initialized = False

def _init_tables():
    global _tables_initialized
    if _tables_initialized:
        return
    ddls = [
        (
            "CREATE TABLE IF NOT EXISTS `{}` "
            "(workspace_id STRING NOT NULL, user_id STRING NOT NULL, "
            "wallet_address STRING NOT NULL, author_identity STRING NOT NULL, "
            "display_name STRING, email STRING, is_public BOOL DEFAULT FALSE, "
            "is_featured BOOL DEFAULT FALSE, featured_rank INT64, "
            "created_at TIMESTAMP, updated_at TIMESTAMP, "
            "tool_count INT64 DEFAULT 0, story_count INT64 DEFAULT 0, "
            "plan STRING DEFAULT 'free')"
        ).format(W_TABLE),
        (
            "CREATE TABLE IF NOT EXISTS `{}` "
            "(story_id STRING NOT NULL, workspace_id STRING NOT NULL, "
            "author_identity STRING NOT NULL, title STRING, summary STRING, "
            "body STRING, tags ARRAY<STRING>, is_public BOOL DEFAULT TRUE, "
            "published_at TIMESTAMP, view_count INT64 DEFAULT 0, "
            "evidence_refs ARRAY<STRING>)"
        ).format(S_TABLE),
        (
            "CREATE TABLE IF NOT EXISTS `{}` "
            "(tool_id STRING NOT NULL, workspace_id STRING NOT NULL, "
            "github_url STRING, tool_name STRING, tool_description STRING, "
            "handler_path STRING, capabilities ARRAY<STRING>, "
            "installed_at TIMESTAMP, status STRING DEFAULT 'active')"
        ).format(T_TABLE),
    ]
    for ddl in ddls:
        try:
            _bq().query(ddl).result()
        except Exception as e:
            logger.warning("Table init warning (may exist): %s", e)
    _tables_initialized = True


def _derive_wallet(user_id: str) -> str:
    h = hashlib.sha256(user_id.encode()).hexdigest()
    return "0x" + h[:40]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── POST /api/workspaces/create ───────────────────────────────────────────────

@workspace_bp.route("/workspaces/create", methods=["POST"])
def create_workspace():
    """
    Create new user account. One signup = one wallet = one workspace = one newspaper identity.
    Body: { display_name, email, is_public? }
    """
    _init_tables()
    data = request.get_json(force=True, silent=True) or {}
    display_name = data.get("display_name", "").strip()
    email = data.get("email", "").strip().lower()
    is_public = bool(data.get("is_public", False))

    if not display_name or not email:
        abort(400, "display_name and email are required")

    user_id        = str(uuid.uuid4())
    workspace_id   = user_id
    wallet_address = _derive_wallet(user_id)
    author_identity = wallet_address
    now = _now_iso()

    row = {
        "workspace_id":    workspace_id,
        "user_id":         user_id,
        "wallet_address":  wallet_address,
        "author_identity": author_identity,
        "display_name":    display_name,
        "email":           email,
        "is_public":       is_public,
        "is_featured":     False,
        "featured_rank":   None,
        "created_at":      now,
        "updated_at":      now,
        "tool_count":      0,
        "story_count":     0,
        "plan":            "free",
    }
    errors = _bq().insert_rows_json(W_TABLE, [row])
    if errors:
        abort(500, "Workspace creation failed: {}".format(errors))

    return jsonify({
        "status":          "created",
        "workspace_id":    workspace_id,
        "wallet_address":  wallet_address,
        "author_identity": author_identity,
        "display_name":    display_name,
        "message":         "workspace = wallet = newspaper. One identity.",
        "created_at":      now,
    }), 201


# ── GET /api/workspaces/<workspace_id> ───────────────────────────────────────

@workspace_bp.route("/workspaces/<workspace_id>", methods=["GET"])
def get_workspace(workspace_id: str):
    _init_tables()
    sql = "SELECT * FROM `{}` WHERE workspace_id = @wid LIMIT 1".format(W_TABLE)
    rows = _run_query(sql, [_bq_param("wid", workspace_id)])
    if not rows:
        abort(404, "Workspace not found")
    return jsonify(rows[0])


# ── GET /api/workspaces/public ────────────────────────────────────────────────

@workspace_bp.route("/workspaces/public", methods=["GET"])
def list_public_workspaces():
    _init_tables()
    sql = (
        "SELECT workspace_id, display_name, author_identity, wallet_address, "
        "is_featured, featured_rank, story_count, tool_count, created_at "
        "FROM `{}` WHERE is_public = TRUE "
        "ORDER BY is_featured DESC, featured_rank ASC NULLS LAST, story_count DESC "
        "LIMIT 100"
    ).format(W_TABLE)
    rows = _run_query(sql)
    return jsonify({"workspaces": rows, "count": len(rows)})


# ── GET /api/newspaper/featured ───────────────────────────────────────────────

@workspace_bp.route("/newspaper/featured", methods=["GET"])
def get_featured_story():
    """Returns Featured Story #1 (builder master workspace). No login required."""
    _init_tables()
    sql = (
        "SELECT s.story_id, s.title, s.summary, s.body, s.tags, "
        "s.published_at, s.view_count, s.evidence_refs, "
        "w.display_name, w.wallet_address, w.author_identity "
        "FROM `{}` s JOIN `{}` w ON s.workspace_id = w.workspace_id "
        "WHERE w.is_featured = TRUE AND w.featured_rank = 1 "
        "ORDER BY s.published_at DESC LIMIT 10"
    ).format(S_TABLE, W_TABLE)
    stories = _run_query(sql)
    return jsonify({
        "featured_workspace": BUILDER_WORKSPACE_ID,
        "featured_wallet":    BUILDER_WALLET,
        "stories":            stories,
        "count":              len(stories),
    })


# ── POST /api/newspaper/publish ───────────────────────────────────────────────

@workspace_bp.route("/newspaper/publish", methods=["POST"])
def publish_story():
    """Publish an investigation as a newspaper story linked to a workspace."""
    _init_tables()
    data = request.get_json(force=True, silent=True) or {}
    workspace_id = data.get("workspace_id", "").strip()
    title = data.get("title", "").strip()
    if not workspace_id or not title:
        abort(400, "workspace_id and title are required")

    sql = "SELECT author_identity FROM `{}` WHERE workspace_id = @wid LIMIT 1".format(W_TABLE)
    ws = _run_query(sql, [_bq_param("wid", workspace_id)])
    if not ws:
        abort(404, "Workspace not found")

    story_id = str(uuid.uuid4())
    now = _now_iso()
    row = {
        "story_id":        story_id,
        "workspace_id":    workspace_id,
        "author_identity": ws[0]["author_identity"],
        "title":           title,
        "summary":         data.get("summary", ""),
        "body":            data.get("body", ""),
        "tags":            data.get("tags", []),
        "is_public":       bool(data.get("is_public", True)),
        "published_at":    now,
        "view_count":      0,
        "evidence_refs":   data.get("evidence_refs", []),
    }
    errors = _bq().insert_rows_json(S_TABLE, [row])
    if errors:
        abort(500, "Publish failed: {}".format(errors))

    def _inc():
        try:
            update_sql = (
                "UPDATE `{}` SET story_count = story_count + 1, "
                "updated_at = '{}' WHERE workspace_id = '{}'"
            ).format(W_TABLE, now, workspace_id)
            _bq().query(update_sql).result()
        except Exception as e:
            logger.warning("story_count increment failed: %s", e)

    threading.Thread(target=_inc, daemon=True).start()
    return jsonify({"status": "published", "story_id": story_id, "published_at": now}), 201


# ── GET /api/workspaces/<id>/stories ─────────────────────────────────────────

@workspace_bp.route("/workspaces/<workspace_id>/stories", methods=["GET"])
def get_workspace_stories(workspace_id: str):
    _init_tables()
    sql = (
        "SELECT story_id, title, summary, tags, published_at, view_count "
        "FROM `{}` WHERE workspace_id = @wid AND is_public = TRUE "
        "ORDER BY published_at DESC LIMIT 50"
    ).format(S_TABLE)
    rows = _run_query(sql, [_bq_param("wid", workspace_id)])
    return jsonify({"workspace_id": workspace_id, "stories": rows, "count": len(rows)})


# ── POST /api/tools/import ────────────────────────────────────────────────────

@workspace_bp.route("/tools/import", methods=["POST"])
def import_tool():
    """
    Import a GitHub repo as an OSINT tool into a user workspace.
    Clones repo, reads plugin.json, registers tool in BQ.
    Body: { workspace_id, github_url }
    """
    _init_tables()
    data = request.get_json(force=True, silent=True) or {}
    workspace_id = data.get("workspace_id", "").strip()
    github_url   = data.get("github_url", "").strip()
    if not workspace_id or not github_url:
        abort(400, "workspace_id and github_url are required")
    if not github_url.startswith("https://github.com/"):
        abort(400, "Only https://github.com/ URLs are supported")
    ws = _run_query(
        "SELECT workspace_id FROM `{}` WHERE workspace_id = @wid LIMIT 1".format(W_TABLE),
        [_bq_param("wid", workspace_id)]
    )
    if not ws:
        abort(404, "Workspace not found")

    tool_id = str(uuid.uuid4())

    def _clone_and_register():
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                result = subprocess.run(
                    ["git", "clone", "--depth=1", github_url, tmpdir],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode != 0:
                    logger.error("git clone failed: %s", result.stderr)
                    return
                manifest = {}
                ppath = os.path.join(tmpdir, "plugin.json")
                if os.path.exists(ppath):
                    with open(ppath) as f:
                        manifest = json.load(f)
                now = _now_iso()
                row = {
                    "tool_id":          tool_id,
                    "workspace_id":     workspace_id,
                    "github_url":       github_url,
                    "tool_name":        manifest.get("name", github_url.split("/")[-1]),
                    "tool_description": manifest.get("description", ""),
                    "handler_path":     manifest.get("handler", "handler.js"),
                    "capabilities":     manifest.get("capabilities", []),
                    "installed_at":     now,
                    "status":           "active",
                }
                errs = _bq().insert_rows_json(T_TABLE, [row])
                if errs:
                    logger.error("Tool BQ insert errors: %s", errs)
                    return
                update_sql = (
                    "UPDATE `{}` SET tool_count = tool_count + 1 "
                    "WHERE workspace_id = '{}'"
                ).format(W_TABLE, workspace_id)
                _bq().query(update_sql).result()
                logger.info("Tool '%s' registered in workspace %s", row["tool_name"], workspace_id)
        except Exception as e:
            logger.error("Tool import error: %s", e)

    threading.Thread(target=_clone_and_register, daemon=True).start()
    return jsonify({
        "status":    "queued",
        "tool_id":   tool_id,
        "github_url": github_url,
        "message":   "Tool import started. Use /api/tools/status/{} to check.".format(tool_id),
    }), 202


# ── GET /api/tools/status/<tool_id> ──────────────────────────────────────────

@workspace_bp.route("/tools/status/<tool_id>", methods=["GET"])
def tool_status(tool_id: str):
    _init_tables()
    rows = _run_query(
        "SELECT * FROM `{}` WHERE tool_id = @tid LIMIT 1".format(T_TABLE),
        [_bq_param("tid", tool_id)]
    )
    if not rows:
        return jsonify({"status": "pending_or_not_found", "tool_id": tool_id})
    return jsonify(rows[0])


# ── GET /api/crypto/public ────────────────────────────────────────────────────

@workspace_bp.route("/crypto/public", methods=["GET"])
def crypto_public():
    """
    Public crypto dashboard — no login required.
    TFT + OSINT tokens visible on TaxFunded and OsintNeoAi main pages.
    """
    tracker_path = os.path.join(
        os.path.dirname(__file__), "..", "crypto_ledger_tracker.json"
    )
    tracker = {}
    try:
        with open(tracker_path) as f:
            tracker = json.load(f)
    except Exception:
        pass

    return jsonify({
        "public":          True,
        "requires_login":  False,
        "tokens": {
            "TFT": {
                "name":     "TaxFunded Token",
                "contract": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "supply":   "14,200,000",
                "symbol":   "TFT",
                "network":  "Ethereum Mainnet",
            },
            "OSINT": {
                "name":     "OSINT Token",
                "contract": "0x123f61a7B14341A67280609320e8A631899120bc",
                "supply":   "50,000,000",
                "symbol":   "OSINT",
                "network":  "Ethereum Mainnet",
            },
            "bridge": {
                "name":       "DualAuditTokenBridge",
                "contract":   "0x99887766554433221100aabbccddeeff00112233",
                "apy":        "12.5%",
                "multiplier": "1.05x",
            },
        },
        "taxfunded_ledger": [b for b in tracker.get("ledger_blocks", []) if "TFT" in b.get("description", "") or b.get("token_symbol") == "TFT"],
        "osint_ledger":     [b for b in tracker.get("ledger_blocks", []) if "OSINT" in b.get("description", "") or b.get("token_symbol") == "OSINT"],
        "metrics":      tracker.get("metrics", {}),
        "last_updated": _now_iso(),
    })


# ── GET /api/crypto/public/ledger-growth ─────────────────────────────────────

@workspace_bp.route("/crypto/public/ledger-growth", methods=["GET"])
def ledger_growth():
    """
    Token value growth index tied to platform activity.
    More workspaces + stories + FOIA = higher token utility / demand.
    Visible on TaxFunded main page without login.
    """
    _init_tables()
    wc_rows = _run_query("SELECT COUNT(*) as cnt FROM `{}` WHERE is_public = TRUE".format(W_TABLE))
    sc_rows = _run_query("SELECT COUNT(*) as cnt FROM `{}` WHERE is_public = TRUE".format(S_TABLE))
    wc = wc_rows[0]["cnt"] if wc_rows else 0
    sc = sc_rows[0]["cnt"] if sc_rows else 0
    tft_idx   = round(1.0 + (wc * 0.00001) + (sc * 0.000005), 6)
    osint_idx = round(1.0 + (wc * 0.000008) + (sc * 0.000003), 6)
    return jsonify({
        "platform_stats": {"public_workspaces": wc, "public_stories": sc},
        "token_growth_index": {"TFT": tft_idx, "OSINT": osint_idx},
        "growth_drivers": [
            "Evidence nodes added to investigation graph",
            "New public workspaces",
            "Newspaper stories published",
            "FOIA submissions filed",
            "GitHub tools imported",
        ],
        "calculated_at": _now_iso(),
    })
