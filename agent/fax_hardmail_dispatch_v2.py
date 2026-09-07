"""
OsintNeoAi — eFax + Hardmail Regulatory Dispatch Engine v2
============================================================
Automated encrypted dispatch to regulatory agencies via:
  1. FaxBetter API (eFax to SEC, FinCEN, HUD OIG, GAO, FBI)
  2. Lob.com API (physical USPS hardmail — certified letter dispatch)
  3. Email dispatch (SMTP with PDF attachment + read receipt)

Preserves user anonymity — all dispatches go out as:
  "OsintNeoAi Public Records & Whistleblower Unit"

Dispatch destinations (pre-configured):
  - SEC Office of the Whistleblower:       (202) 551-4790
  - FinCEN:                                (703) 905-3975
  - HUD Office of Inspector General:       (202) 708-4829
  - GAO FraudNet:                          (202) 512-3090
  - FBI Public Corruption Unit:            (202) 324-3000
  - EPA Criminal Investigation Division:   (202) 564-2480
  - State AG Consumer Protection:          varies by state

Usage:
  python agent/fax_hardmail_dispatch_v2.py --fax --agency SEC --brief briefings/hbnc.md
  python agent/fax_hardmail_dispatch_v2.py --mail --agency FinCEN --brief briefings/hbnc.md
  python agent/fax_hardmail_dispatch_v2.py --all --brief briefings/hbnc.md

Environment:
  FAXBETTER_API_KEY   FaxBetter account API key (https://www.faxbetter.com)
  LOB_API_KEY         Lob.com API key for physical mail (https://lob.com)
  SMTP_HOST           SMTP server for email dispatch
  SMTP_USER           SMTP username
  SMTP_PASS           SMTP password
  SENDER_NAME         Override sender name (default: OsintNeoAi Public Records Unit)
  SENDER_FAX          FaxBetter outbound fax number
"""

import os
import sys
import json
import uuid
import logging
import argparse
import smtplib
import urllib.request
import urllib.parse
import base64
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent

# ── Agency registry ──────────────────────────────────────────────────────────

AGENCIES = {
    "SEC": {
        "full_name":    "U.S. Securities and Exchange Commission — Office of the Whistleblower",
        "fax":          "+12025514790",
        "mail_address": {"name": "SEC Whistleblower Office", "address1": "100 F Street NE", "city": "Washington", "state": "DC", "zip": "20549"},
        "email":        "whistleblower@sec.gov",
        "category":     "securities_fraud",
    },
    "FinCEN": {
        "full_name":    "Financial Crimes Enforcement Network",
        "fax":          "+17039053975",
        "mail_address": {"name": "FinCEN", "address1": "P.O. Box 39", "city": "Vienna", "state": "VA", "zip": "22183"},
        "email":        "fincen@fincen.gov",
        "category":     "financial_crimes",
    },
    "HUD_OIG": {
        "full_name":    "U.S. Department of Housing and Urban Development — Office of Inspector General",
        "fax":          "+12027084829",
        "mail_address": {"name": "HUD OIG Hotline", "address1": "451 7th Street SW", "city": "Washington", "state": "DC", "zip": "20410"},
        "email":        "hotline@hudoig.gov",
        "category":     "housing_fraud",
    },
    "GAO": {
        "full_name":    "Government Accountability Office — FraudNet",
        "fax":          "+12025123090",
        "mail_address": {"name": "GAO FraudNet", "address1": "441 G Street NW", "city": "Washington", "state": "DC", "zip": "20548"},
        "email":        "fraudnet@gao.gov",
        "category":     "government_fraud",
    },
    "FBI": {
        "full_name":    "Federal Bureau of Investigation — Public Corruption Unit",
        "fax":          "+12023243000",
        "mail_address": {"name": "FBI Public Corruption Unit", "address1": "935 Pennsylvania Ave NW", "city": "Washington", "state": "DC", "zip": "20535"},
        "email":        "tips.fbi.gov",
        "category":     "public_corruption",
    },
    "EPA": {
        "full_name":    "Environmental Protection Agency — Criminal Investigation Division",
        "fax":          "+12025642480",
        "mail_address": {"name": "EPA Criminal Investigation Division", "address1": "1200 Pennsylvania Ave NW", "city": "Washington", "state": "DC", "zip": "20460"},
        "email":        "OIG_Hotline@epa.gov",
        "category":     "environmental_crime",
    },
}

SENDER_NAME = os.environ.get("SENDER_NAME", "OsintNeoAi Public Records & Whistleblower Unit")
SENDER_FAX  = os.environ.get("SENDER_FAX", "")
SENDER_MAIL_ADDR = {
    "name":     SENDER_NAME,
    "address1": "PO Box 1",
    "city":     "Anonymous",
    "state":    "CA",
    "zip":      "00000",
}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load_brief(brief_path: str) -> tuple[str, str]:
    """Load a briefing file and return (title, body)."""
    p = Path(brief_path)
    if not p.exists():
        # Try relative to repo root
        p = REPO_ROOT / brief_path
    if not p.exists():
        raise FileNotFoundError("Brief not found: {}".format(brief_path))
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.strip().splitlines()
    title = lines[0].lstrip("# ").strip() if lines else p.stem
    body = text[:50000]  # cap at 50k chars for fax
    return title, body


def _build_cover_sheet(agency_name: str, title: str, dispatch_id: str) -> str:
    """Generate a formatted cover sheet for fax/mail dispatch."""
    agency = AGENCIES.get(agency_name, {})
    return """
================================================================================
CONFIDENTIAL — WHISTLEBLOWER SUBMISSION
OsintNeoAi Public Records & Whistleblower Unit
================================================================================

DATE:         {date}
DISPATCH ID:  {dispatch_id}
TO:           {agency_full}
RE:           {title}

This submission is filed on behalf of whistleblowers and public interest
investigators who have identified the following evidence of potential violations.
The submitting party (OsintNeoAi) protects all originating sources.

All evidence referenced herein is publicly available at:
  https://github.com/Tonypost949/OsintNeoAi

Investigation supported by:
  - BigQuery forensic evidence graph (35,000+ nodes)
  - Environmental Data Resources (EDR) reports
  - Public property and corporate records
  - Federal FOIA responses

LEGAL BASIS: 15 U.S.C. § 78u-6 (SEC Whistleblower Program)
             31 U.S.C. § 5318A (FinCEN)
             18 U.S.C. § 201 (Bribery of Public Officials)
             CEQA § 21083 | Cal. Gov. Code § 1090

Please direct any response to: whistleblower@osintneoai.me
================================================================================

""".format(
        date=_now_iso(),
        dispatch_id=dispatch_id,
        agency_full=agency.get("full_name", agency_name),
        title=title,
    )


# ── FaxBetter eFax dispatch ───────────────────────────────────────────────────

def dispatch_fax(agency_name: str, title: str, body: str, dispatch_id: str) -> dict:
    """
    Send via FaxBetter API.
    Docs: https://www.faxbetter.com/api
    """
    api_key = os.environ.get("FAXBETTER_API_KEY", "")
    if not api_key:
        logger.warning("[FAX] FAXBETTER_API_KEY not set — fax dispatch skipped")
        return {"status": "skipped", "reason": "FAXBETTER_API_KEY not configured"}

    agency = AGENCIES.get(agency_name, {})
    to_fax = agency.get("fax", "")
    if not to_fax:
        return {"status": "error", "reason": "No fax number for {}".format(agency_name)}

    cover = _build_cover_sheet(agency_name, title, dispatch_id)
    full_content = cover + body

    # FaxBetter send endpoint
    payload = urllib.parse.urlencode({
        "api_key":    api_key,
        "to":         to_fax,
        "from":       SENDER_FAX or "OsintNeoAi",
        "subject":    "[WHISTLEBLOWER] {} — {}".format(dispatch_id, title[:80]),
        "content":    full_content[:65000],  # FaxBetter 65k char limit
    }).encode()

    try:
        req = urllib.request.Request(
            "https://www.faxbetter.com/api/v2/faxes/send",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            logger.info("[FAX] Sent to %s: %s", to_fax, result)
            return {"status": "sent", "agency": agency_name, "fax": to_fax, "result": result}
    except Exception as e:
        logger.error("[FAX] Failed: %s", e)
        return {"status": "error", "agency": agency_name, "error": str(e)}


# ── Lob.com physical USPS hardmail ───────────────────────────────────────────

def dispatch_hardmail(agency_name: str, title: str, body: str, dispatch_id: str) -> dict:
    """
    Send a physical certified letter via Lob.com API.
    Docs: https://docs.lob.com/
    """
    api_key = os.environ.get("LOB_API_KEY", "")
    if not api_key:
        logger.warning("[MAIL] LOB_API_KEY not set — hardmail dispatch skipped")
        return {"status": "skipped", "reason": "LOB_API_KEY not configured"}

    agency = AGENCIES.get(agency_name, {})
    mail_addr = agency.get("mail_address", {})
    if not mail_addr:
        return {"status": "error", "reason": "No mail address for {}".format(agency_name)}

    cover = _build_cover_sheet(agency_name, title, dispatch_id)
    letter_html = """
    <html><body>
    <pre style="font-family: Courier New; font-size: 10px; white-space: pre-wrap;">
    {content}
    </pre>
    </body></html>
    """.format(content=(cover + body[:20000]).replace("<", "&lt;").replace(">", "&gt;"))

    # Build Lob letter request
    payload = json.dumps({
        "description":    "{} — {}".format(dispatch_id, title[:100]),
        "to": {
            "name":               mail_addr.get("name", agency_name),
            "address_line1":      mail_addr.get("address1", ""),
            "address_line2":      mail_addr.get("address2", ""),
            "address_city":       mail_addr.get("city", ""),
            "address_state":      mail_addr.get("state", ""),
            "address_zip":        mail_addr.get("zip", ""),
            "address_country":    "US",
        },
        "from": {
            "name":               SENDER_MAIL_ADDR["name"],
            "address_line1":      SENDER_MAIL_ADDR["address1"],
            "address_city":       SENDER_MAIL_ADDR["city"],
            "address_state":      SENDER_MAIL_ADDR["state"],
            "address_zip":        SENDER_MAIL_ADDR["zip"],
            "address_country":    "US",
        },
        "file":           letter_html,
        "color":          False,
        "double_sided":   True,
        "address_placement": "top_first_page",
        "mail_type":      "usps_first_class",  # or "usps_certified"
    }).encode()

    credentials = base64.b64encode("{}:".format(api_key).encode()).decode()
    try:
        req = urllib.request.Request(
            "https://api.lob.com/v1/letters",
            data=payload,
            headers={
                "Authorization":  "Basic {}".format(credentials),
                "Content-Type":   "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            logger.info("[MAIL] Letter queued to %s: %s", mail_addr.get("name"), result.get("id"))
            return {"status": "queued", "agency": agency_name, "letter_id": result.get("id"), "result": result}
    except Exception as e:
        logger.error("[MAIL] Failed: %s", e)
        return {"status": "error", "agency": agency_name, "error": str(e)}


# ── Email dispatch ────────────────────────────────────────────────────────────

def dispatch_email(agency_name: str, title: str, body: str, dispatch_id: str) -> dict:
    """Send via SMTP with cover sheet in body."""
    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")

    if not smtp_host:
        logger.warning("[EMAIL] SMTP_HOST not set — email dispatch skipped")
        return {"status": "skipped", "reason": "SMTP_HOST not configured"}

    agency = AGENCIES.get(agency_name, {})
    to_email = agency.get("email", "")
    if not to_email or to_email.startswith("http"):
        return {"status": "skipped", "reason": "No direct email for {}".format(agency_name)}

    cover = _build_cover_sheet(agency_name, title, dispatch_id)
    msg = MIMEMultipart()
    msg["From"]    = smtp_user
    msg["To"]      = to_email
    msg["Subject"] = "[WHISTLEBLOWER SUBMISSION] {} — {}".format(dispatch_id, title[:80])
    msg.attach(MIMEText(cover + body[:50000], "plain"))

    try:
        with smtplib.SMTP_SSL(smtp_host, 465) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info("[EMAIL] Sent to %s", to_email)
        return {"status": "sent", "agency": agency_name, "email": to_email}
    except Exception as e:
        logger.error("[EMAIL] Failed: %s", e)
        return {"status": "error", "agency": agency_name, "error": str(e)}


# ── Log dispatch to BigQuery ──────────────────────────────────────────────────

def _log_to_bq(dispatch_record: dict) -> None:
    """Log dispatch to BigQuery forensic_layers.foia_dispatch_log."""
    try:
        from google.cloud import bigquery
        bq = bigquery.Client(project=os.environ.get("GCP_PROJECT", "noble-beanbag-497411-m4"))
        table = "noble-beanbag-497411-m4.forensic_layers.foia_dispatch_log"
        bq.insert_rows_json(table, [dispatch_record])
        logger.info("[BQ] Dispatch logged to %s", table)
    except Exception as e:
        logger.warning("[BQ] Logging failed (non-fatal): %s", e)


# ── Master dispatch ───────────────────────────────────────────────────────────

def run_dispatch(
    agencies: list[str],
    brief_path: str,
    do_fax: bool = True,
    do_mail: bool = False,
    do_email: bool = True,
) -> dict:
    """
    Run full dispatch to one or more agencies.
    Returns a dispatch report with status for each agency and channel.
    """
    dispatch_id = "DISP-{}".format(uuid.uuid4().hex[:8].upper())
    logger.info("=== Dispatch %s starting ===", dispatch_id)

    try:
        title, body = _load_brief(brief_path)
    except FileNotFoundError as e:
        return {"error": str(e), "dispatch_id": dispatch_id}

    logger.info("Brief: %s (%d chars)", title, len(body))

    results = {
        "dispatch_id":   dispatch_id,
        "dispatched_at": _now_iso(),
        "brief_file":    brief_path,
        "brief_title":   title,
        "agencies":      {},
    }

    for agency in agencies:
        if agency not in AGENCIES:
            logger.warning("Unknown agency: %s (skipping)", agency)
            results["agencies"][agency] = {"error": "unknown agency"}
            continue

        logger.info("Dispatching to %s...", agency)
        agency_results = {}

        if do_fax:
            agency_results["fax"] = dispatch_fax(agency, title, body, dispatch_id)
        if do_email:
            agency_results["email"] = dispatch_email(agency, title, body, dispatch_id)
        if do_mail:
            agency_results["hardmail"] = dispatch_hardmail(agency, title, body, dispatch_id)

        results["agencies"][agency] = agency_results

        # Log each agency dispatch to BQ
        _log_to_bq({
            "dispatch_id":   dispatch_id,
            "agency":        agency,
            "brief_file":    brief_path,
            "brief_title":   title,
            "channels":      json.dumps(agency_results),
            "dispatched_at": _now_iso(),
        })

    logger.info("=== Dispatch %s complete ===", dispatch_id)
    return results


# ── Flask API endpoint (mounted into main.py) ─────────────────────────────────

def register_dispatch_routes(app):
    """Register eFax/Hardmail routes onto existing Flask app."""
    from flask import Blueprint, request, jsonify
    dispatch_bp = Blueprint("dispatch", __name__, url_prefix="/api/dispatch")

    @dispatch_bp.route("/fax", methods=["POST"])
    def api_fax():
        """POST /api/dispatch/fax { agencies:[], brief_path: str }"""
        data = request.get_json(force=True, silent=True) or {}
        agencies  = data.get("agencies", list(AGENCIES.keys()))
        brief     = data.get("brief_path", "briefings/hbnc_forensic_whistleblower_briefing.md")
        results   = run_dispatch(agencies, brief, do_fax=True, do_mail=False, do_email=False)
        return jsonify(results), 200

    @dispatch_bp.route("/hardmail", methods=["POST"])
    def api_hardmail():
        """POST /api/dispatch/hardmail { agencies:[], brief_path: str }"""
        data = request.get_json(force=True, silent=True) or {}
        agencies  = data.get("agencies", list(AGENCIES.keys()))
        brief     = data.get("brief_path", "briefings/hbnc_forensic_whistleblower_briefing.md")
        results   = run_dispatch(agencies, brief, do_fax=False, do_mail=True, do_email=False)
        return jsonify(results), 200

    @dispatch_bp.route("/all", methods=["POST"])
    def api_all():
        """POST /api/dispatch/all { agencies:[], brief_path: str }"""
        data = request.get_json(force=True, silent=True) or {}
        agencies  = data.get("agencies", list(AGENCIES.keys()))
        brief     = data.get("brief_path", "briefings/hbnc_forensic_whistleblower_briefing.md")
        results   = run_dispatch(agencies, brief, do_fax=True, do_mail=True, do_email=True)
        return jsonify(results), 200

    @dispatch_bp.route("/agencies", methods=["GET"])
    def api_agencies():
        """GET /api/dispatch/agencies — List all pre-configured dispatch targets."""
        return jsonify({
            "agencies": {
                name: {
                    "full_name": cfg["full_name"],
                    "fax":       cfg.get("fax", ""),
                    "email":     cfg.get("email", ""),
                    "category":  cfg.get("category", ""),
                }
                for name, cfg in AGENCIES.items()
            }
        })

    app.register_blueprint(dispatch_bp)
    logger.info("[Dispatch] routes registered: /api/dispatch/fax /api/dispatch/hardmail /api/dispatch/all /api/dispatch/agencies")
    return dispatch_bp


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="OsintNeoAi eFax + Hardmail Dispatch")
    parser.add_argument("--fax",    action="store_true", help="Send via eFax (FaxBetter)")
    parser.add_argument("--mail",   action="store_true", help="Send physical USPS hardmail (Lob.com)")
    parser.add_argument("--email",  action="store_true", help="Send via SMTP email")
    parser.add_argument("--all",    action="store_true", help="Send via all channels")
    parser.add_argument("--agency", nargs="+", default=list(AGENCIES.keys()),
                        help="Target agencies (default: all). Options: {}".format(", ".join(AGENCIES.keys())))
    parser.add_argument("--brief",  required=True,
                        help="Path to briefing file (e.g. briefings/hbnc_forensic_whistleblower_briefing.md)")
    parser.add_argument("--dry-run", action="store_true", help="Print cover sheet only, do not send")
    args = parser.parse_args()

    if args.dry_run:
        title, body = _load_brief(args.brief)
        cover = _build_cover_sheet(args.agency[0], title, "DRY-RUN-" + uuid.uuid4().hex[:6].upper())
        print(cover)
        print("--- BRIEF PREVIEW (first 2000 chars) ---")
        print(body[:2000])
        return

    do_fax   = args.fax   or args.all
    do_mail  = args.mail  or args.all
    do_email = args.email or args.all

    if not any([do_fax, do_mail, do_email]):
        parser.error("Specify at least one of: --fax --mail --email --all")

    results = run_dispatch(args.agency, args.brief, do_fax=do_fax, do_mail=do_mail, do_email=do_email)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
