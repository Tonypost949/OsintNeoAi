#!/usr/bin/env python3
"""
scripts/auto_leads_correlation_v2.py
====================================
Cloud-Automated Leads Data Correlation Engine — 100% Cloud Autonomous
Runs in Azure App Service (background thread) + GitHub Actions (scheduled)

Features:
- Scans repo knowledge graph (nodes.json / edges.json) without BigQuery dependency
- Ingests and normalizes whistleblower tips and mutual aid cases (evidence/mutual_aid_cases.json)
- Detects 6+ lead vectors: PPP+Property overlap, multi-ORG persons, same-address shells,
  high-risk PPP orgs, litigation exposure, CHDO/straw-buyer nexus, mutual aid intake leads
- Computes dynamic spatial proximity to 288 Caltrans District 12 CCTV cameras
- Outputs structured JSON to data/leads_feed.json (live API) + timestamped reports/auto_leads/
- Updates logs/correlation_runs.log for audit trail
- Idempotent, safe to run every hour in cloud (no secrets, no writes outside repo)
"""
import os
import sys
import json
import glob
import time
import math
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional, Tuple

# Resolve dynamic repo root
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1] if THIS_FILE.parents[1].name != "scripts" else THIS_FILE.parents[1]
if not (REPO_ROOT / "nodes.json").exists():
    for cand in [Path("/home/site/wwwroot"), Path("C:/OsintNeoAi"), Path.cwd()]:
        if (cand / "nodes.json").exists():
            REPO_ROOT = cand
            break

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

NODES_PATH = REPO_ROOT / "nodes.json"
EDGES_PATH = REPO_ROOT / "edges.json"
TASKS_PATH = REPO_ROOT / "data" / "tasks.json"
MUTUAL_AID_PATH = REPO_ROOT / "evidence" / "mutual_aid_cases.json"
CCTV_GEOJSON = REPO_ROOT / "evidence" / "caltrans_d12_cctv.geojson"
LEADS_FEED_PATH = REPO_ROOT / "data" / "leads_feed.json"
REPORTS_DIR = REPO_ROOT / "reports" / "auto_leads"
LOG_PATH = REPO_ROOT / "logs" / "correlation_runs.log"

KNOWN_GEO_ANCHORS = {
    "1601 DOVE": (33.6558, -117.8682),
    "DOVE STREET": (33.6558, -117.8682),
    "17631 CAMERON": (33.7028, -117.9944),
    "CAMERON LANE": (33.7028, -117.9944),
    "7561 CENTER": (33.7389, -118.0016),
    "CENTER AVE": (33.7389, -118.0016),
    "17642 BEACH": (33.7029, -117.9892),
    "BEACH BLVD": (33.7029, -117.9892),
    "MAGNOLIA": (33.6914, -117.9731),
    "ASCON": (33.6521, -117.9839),
    "HUNTINGTON BEACH": (33.6595, -117.9988),
    "NEWPORT BEACH": (33.6189, -117.9289),
    "ANAHEIM": (33.8366, -117.9143),
    "SANTA ANA": (33.7455, -117.8677),
    "IRVINE": (33.6846, -117.8265),
    "ORANGE COUNTY": (33.7175, -117.8311),
}


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as lf:
            lf.write(line + "\n")
    except Exception:
        pass


def load_json(path: Path, default=None) -> Any:
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
                if not content:
                    return default
                try:
                    return json.loads(content)
                except Exception:
                    items = []
                    for match in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content, re.DOTALL):
                        try: items.append(json.loads(match.group(0)))
                        except Exception: pass
                    if items:
                        return items
    except Exception as e:
        log(f"WARN load {path}: {e}")
    return default


def normalize_name(name: Optional[str]) -> str:
    if not name: return ""
    cleaned = str(name).upper().strip()
    for suff in [r"\bLLC\b", r"\bINC\b", r"\bCORP\b", r"\bLP\b", r"\bLTD\b", r"\bCO\b", r"\bCOMPANY\b"]:
        cleaned = re.sub(suff, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[-.,&/()'\"]", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def normalize_apn(apn: Optional[str]) -> str:
    if not apn: return ""
    cleaned = re.sub(r"\b(APN|PARCEL|NO|NUMBER)\b[:#\s]*", "", str(apn), flags=re.IGNORECASE)
    raw = re.sub(r"[^0-9A-Za-z]", "", cleaned).upper()
    if len(raw) == 8 and raw.isdigit():
        return f"{raw[0:3]}-{raw[3:6]}-{raw[6:8]}"
    elif len(raw) == 10 and raw.isdigit():
        return f"{raw[0:3]}-{raw[3:6]}-{raw[6:10]}"
    return raw


def normalize_address(address: Optional[str]) -> str:
    if not address: return ""
    addr = str(address).upper().strip()
    addr = re.sub(r"#\s*", "UNIT ", addr)
    addr = addr.replace(".", " ")
    for k, v in [
        (r"\bST\b", "STREET"), (r"\bAVE\b", "AVENUE"), (r"\bBLVD\b", "BOULEVARD"),
        (r"\bRD\b", "ROAD"), (r"\bLN\b", "LANE"), (r"\bCT\b", "COURT"),
        (r"\bDR\b", "DRIVE"), (r"\bWAY\b", "WAY"), (r"\bPKWY\b", "PARKWAY"),
        (r"\bCIR\b", "CIRCLE"), (r"\bHWY\b", "HIGHWAY"), (r"\bSTE\b", "SUITE"),
        (r"\bAPT\b", "APARTMENT"), (r"\bN\b", "NORTH"), (r"\bS\b", "SOUTH"),
        (r"\bE\b", "EAST"), (r"\bW\b", "WEST"), (r"\bNE\b", "NORTHEAST"),
        (r"\bNW\b", "NORTHWEST"), (r"\bSE\b", "SOUTHEAST"), (r"\bSW\b", "SOUTHWEST")
    ]:
        addr = re.sub(k, v, addr)
    addr = re.sub(r"\s+", " ", addr).strip()
    return re.sub(r"\s*,\s*", ", ", addr)


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3958.8
    try:
        phi1, phi2 = math.radians(float(lat1)), math.radians(float(lat2))
        dphi = math.radians(float(lat2) - float(lat1))
        dlambda = math.radians(float(lon2) - float(lon1))
        a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
        a = min(1.0, max(0.0, a))
        return R * (2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)))
    except Exception:
        return 9999.0


def load_cctv_cameras() -> List[Dict[str, Any]]:
    cameras = []
    geojson_cand = CCTV_GEOJSON
    if not geojson_cand.exists():
        for cand in [REPO_ROOT / "public" / "caltrans_d12_cctv.geojson", REPO_ROOT / "opencode_work" / "caltrans_d12_cctv.geojson"]:
            if cand.exists():
                geojson_cand = cand
                break
    if geojson_cand.exists():
        try:
            with open(geojson_cand, "r", encoding="utf-8") as f:
                cctv_data = json.load(f)
            for feat in cctv_data.get("features", []):
                props = feat.get("properties", {})
                coords = feat.get("geometry", {}).get("coordinates", [0.0, 0.0])
                cam_id = str(props.get("object_id") or props.get("id") or props.get("cctv_id") or "")
                location = str(props.get("entity_name") or props.get("locationName") or props.get("name") or "Caltrans CCTV")
                cameras.append({
                    "id": cam_id,
                    "location": location,
                    "route": str(props.get("route") or ""),
                    "direction": str(props.get("direction") or ""),
                    "postmile": props.get("postmile"),
                    "stream_url": props.get("stream_url") or props.get("streamingVideoURL"),
                    "image_url": props.get("image_url") or props.get("currentImageURL"),
                    "lon": float(coords[0]),
                    "lat": float(coords[1])
                })
        except Exception as e:
            log(f"WARN loading CCTV GeoJSON: {e}")
    return cameras


def find_nearest_cctv(lat: Optional[float], lon: Optional[float], cameras: List[Dict[str, Any]], k: int = 3) -> List[Dict[str, Any]]:
    if not cameras or lat is None or lon is None:
        return []
    res = []
    for cam in cameras:
        d = haversine_miles(lat, lon, cam["lat"], cam["lon"])
        res.append({
            "camera_id": cam["id"],
            "location_name": cam["location"],
            "route": cam["route"],
            "direction": cam["direction"],
            "distance_miles": round(d, 2),
            "stream_url": cam["stream_url"],
            "image_url": cam["image_url"],
            "lat": cam["lat"],
            "lon": cam["lon"]
        })
    res.sort(key=lambda x: x["distance_miles"])
    return res[:k]


def geocode_hint(text: str) -> Optional[Tuple[float, float]]:
    if not text: return None
    upper = text.upper()
    for key, coords in KNOWN_GEO_ANCHORS.items():
        if key in upper:
            return coords
    return None


def run_correlation() -> Dict[str, Any]:
    started = datetime.now(timezone.utc)
    log(f"=== AUTO LEADS CORRELATION START {started.isoformat()} repo:{REPO_ROOT} ===")

    cctv_cameras = load_cctv_cameras()
    log(f"Loaded {len(cctv_cameras)} Caltrans CCTV cameras")

    nodes = load_json(NODES_PATH, [])
    edges = load_json(EDGES_PATH, [])
    if isinstance(nodes, dict): nodes = nodes.get("nodes", nodes.get("data", []))
    if isinstance(edges, dict): edges = edges.get("edges", edges.get("links", []))
    if not isinstance(nodes, list): nodes = []
    if not isinstance(edges, list): edges = []

    log(f"Loaded {len(nodes):,} nodes, {len(edges):,} edges")

    nm = {}
    for n in nodes:
        if isinstance(n, dict):
            nid = n.get("id") or n.get("_id") or n.get("properties", {}).get("id")
            if nid: nm[nid] = n

    def nd(edge, side):
        sid = edge.get(f"{side}_id") or edge.get(side)
        if isinstance(sid, dict): sid = sid.get("id")
        return nm.get(sid) if sid else None

    def ntype(n):
        if not isinstance(n, dict): return ""
        return n.get("label") or n.get("type") or n.get("properties", {}).get("type", "")

    def nprops(n):
        return n.get("properties", {}) if isinstance(n.get("properties"), dict) else n

    leads = []
    summary = {}

    # 1. PPP + Property overlap
    ppp_orgs = set()
    prop_orgs = set()
    for e in edges:
        if not isinstance(e, dict): continue
        et = e.get("type") or e.get("label", "")
        s = nd(e, "source")
        t = nd(e, "target")
        if et == "RECEIVED_PPP" and s and ntype(s) == "ORGANIZATION":
            sid = e.get("source_id") or e.get("source")
            if isinstance(sid, dict): sid = sid.get("id")
            if sid: ppp_orgs.add(sid)
        if et == "OWNS" and t and ntype(t) == "PROPERTY":
            sid = e.get("source_id") or e.get("source")
            if isinstance(sid, dict): sid = sid.get("id")
            if sid: prop_orgs.add(sid)

    overlap = ppp_orgs & prop_orgs
    summary["ppp_property_overlap_count"] = len(overlap)
    summary["ppp_orgs_total"] = len(ppp_orgs)
    summary["property_orgs_total"] = len(prop_orgs)

    for oid in sorted(list(overlap))[:20]:
        n = nm.get(oid, {})
        p = nprops(n)
        addr = normalize_address(p.get("address") or p.get("street") or "")
        coords = geocode_hint(addr) or geocode_hint(p.get("city") or "")
        cctv_prox = find_nearest_cctv(coords[0], coords[1], cctv_cameras, k=3) if coords else []
        
        leads.append({
            "vector": "PPP_PROPERTY_OVERLAP",
            "severity": "CRITICAL" if str(p.get("risk_score","")).strip() not in ("", "0", "0.0", "None") else "HIGH",
            "entity_id": oid,
            "entity_name": p.get("name", oid[:40]),
            "address": addr if addr else None,
            "risk_score": p.get("risk_score"),
            "flagged_reason": p.get("flagged_reason"),
            "proximity_cctv": cctv_prox,
            "evidence": "RECEIVED_PPP + OWNS(PROPERTY) in knowledge graph"
        })
    log(f"Vector PPP+Property: {len(overlap)} leads ({len([l for l in leads if l['vector']=='PPP_PROPERTY_OVERLAP'])} exported)")

    # 2. Persons in 2+ ORGs
    po = defaultdict(set)
    for e in edges:
        if not isinstance(e, dict): continue
        if e.get("type") in ("OFFICER_OF", "OWNS", "DIRECTOR_OF", "MEMBER_OF"):
            s = nd(e, "source"); t = nd(e, "target")
            if s and t and ntype(s) == "PERSON" and ntype(t) == "ORGANIZATION":
                sid = e.get("source_id") or e.get("source")
                tid = e.get("target_id") or e.get("target")
                if isinstance(sid, dict): sid = sid.get("id")
                if isinstance(tid, dict): tid = tid.get("id")
                if sid and tid: po[sid].add(tid)
    multi = {k: v for k, v in po.items() if len(v) >= 2}
    summary["multi_org_persons_count"] = len(multi)

    for pid, orgs in sorted(multi.items(), key=lambda x: -len(x[1]))[:15]:
        n = nm.get(pid, {})
        p = nprops(n)
        org_names = []
        for oid in list(orgs)[:4]:
            on = nm.get(oid, {})
            org_names.append(nprops(on).get("name", oid[:24]))
        leads.append({
            "vector": "MULTI_ORG_PERSON",
            "severity": "CRITICAL" if len(orgs) >= 5 else ("HIGH" if len(orgs) >= 3 else "MEDIUM"),
            "person_id": pid,
            "person_name": p.get("name", pid[:40]),
            "org_count": len(orgs),
            "org_sample": org_names,
            "evidence": f"Controls {len(orgs)} orgs via OFFICER_OF/DIRECTOR_OF"
        })
    log(f"Vector MULTI_ORG_PERSON: {len(multi)} persons")

    # 3. Same-address shell clusters
    ao = defaultdict(list)
    for e in edges:
        if not isinstance(e, dict): continue
        if e.get("type") == "REGISTERED_AT":
            t = nd(e, "target"); s = nd(e, "source")
            if t and s and ntype(t) == "ADDRESS" and ntype(s) == "ORGANIZATION":
                tp = nprops(t)
                street = tp.get("street") or tp.get("address") or tp.get("full_address") or t.get("id", "")
                street = normalize_address(str(street).strip())
                if street:
                    sid = e.get("source_id") or e.get("source")
                    if isinstance(sid, dict): sid = sid.get("id")
                    if sid: ao[street].append(sid)
    clusters = {a: orgs for a, orgs in ao.items() if len(orgs) >= 3}
    summary["address_clusters_count"] = len(clusters)

    for addr, orgs in sorted(clusters.items(), key=lambda x: -len(x[1]))[:10]:
        sample_names = []
        for oid in orgs[:4]:
            on = nm.get(oid, {})
            sample_names.append(nprops(on).get("name", oid[:22]))
        coords = geocode_hint(addr)
        cctv_prox = find_nearest_cctv(coords[0], coords[1], cctv_cameras, k=3) if coords else []
        leads.append({
            "vector": "ADDRESS_SHELL_CLUSTER",
            "severity": "CRITICAL" if len(orgs) >= 5 else "HIGH",
            "address": addr[:120],
            "org_count": len(orgs),
            "org_sample": sample_names,
            "proximity_cctv": cctv_prox,
            "evidence": f"{len(orgs)} ORGs REGISTERED_AT same ADDRESS"
        })
    log(f"Vector ADDRESS_SHELL_CLUSTER: {len(clusters)} clusters")

    # 4. High-risk flagged ORGs with PPP
    hr_count = 0
    for oid in ppp_orgs:
        n = nm.get(oid)
        if not n: continue
        p = nprops(n)
        r = str(p.get("risk_score", "")).strip()
        f = str(p.get("flagged_reason", "")).strip()
        if r not in ("", "nan", "None", "0", "0.0") or f not in ("", "nan", "None"):
            hr_count += 1
            if len([l for l in leads if l["vector"] == "HIGH_RISK_PPP"]) < 15:
                leads.append({
                    "vector": "HIGH_RISK_PPP",
                    "severity": "CRITICAL",
                    "entity_id": oid,
                    "entity_name": p.get("name", oid[:40]),
                    "risk_score": p.get("risk_score"),
                    "flagged_reason": p.get("flagged_reason"),
                    "evidence": "RECEIVED_PPP + risk_score/flagged_reason present"
                })
    summary["high_risk_ppp_count"] = hr_count
    log(f"Vector HIGH_RISK_PPP: {hr_count} orgs")

    # 5. Litigation exposure
    lit_persons = set()
    for e in edges:
        if not isinstance(e, dict): continue
        if e.get("type") == "LITIGANT_IN":
            s = nd(e, "source")
            if s and ntype(s) == "PERSON":
                sid = e.get("source_id") or e.get("source")
                if isinstance(sid, dict): sid = sid.get("id")
                if sid: lit_persons.add(sid)
    summary["litigation_persons_count"] = len(lit_persons)

    pd = Counter()
    for e in edges:
        if not isinstance(e, dict): continue
        for side in ("source", "target"):
            sid = e.get(f"{side}_id") or e.get(side)
            if isinstance(sid, dict): sid = sid.get("id")
            if sid and sid in lit_persons:
                pd[sid] += 1
    for pid, deg in pd.most_common(5):
        n = nm.get(pid, {})
        leads.append({
            "vector": "LITIGATION_EXPOSURE",
            "severity": "MEDIUM",
            "person_id": pid,
            "person_name": nprops(n).get("name", pid[:40]),
            "connections": deg,
            "evidence": "LITIGANT_IN edge present + high connectivity"
        })
    log(f"Vector LITIGATION: {len(lit_persons)} persons")

    # 6. Ingest Whistleblower Mutual Aid Cases (evidence/mutual_aid_cases.json)
    mutual_cases = load_json(MUTUAL_AID_PATH, [])
    if isinstance(mutual_cases, list):
        summary["mutual_aid_leads_count"] = len(mutual_cases)
        for mc in mutual_cases:
            if not isinstance(mc, dict): continue
            cid = mc.get("id") or mc.get("case_id") or "CASE-0001"
            vname = mc.get("victim_name") or mc.get("entity_name") or "Anonymous"
            norm_vname = normalize_name(vname)
            loc = mc.get("location") or mc.get("address") or ""
            norm_loc = normalize_address(loc)
            apn = normalize_apn(mc.get("apn") or "")
            summary_txt = mc.get("summary", "")
            itype = mc.get("incident_type", "Whistleblower Retaliation")
            
            lat = mc.get("lat") or mc.get("latitude")
            lon = mc.get("lon") or mc.get("longitude")
            if lat is None or lon is None:
                coords = geocode_hint(norm_loc) or geocode_hint(summary_txt)
                if coords: lat, lon = coords
                    
            cctv_prox = find_nearest_cctv(lat, lon, cctv_cameras, k=3) if (lat is not None and lon is not None) else []
            
            graph_matched = False
            for nid, node in nm.items():
                np_name = normalize_name(nprops(node).get("name", ""))
                if norm_vname and norm_vname != "ANONYMOUS" and np_name and norm_vname in np_name:
                    graph_matched = True
                    break
                    
            leads.append({
                "vector": "CHDO_STRAW_BUYER_NEXUS" if "chdo" in summary_txt.lower() or "straw" in summary_txt.lower() else "MUTUAL_AID_LEAD",
                "severity": "CRITICAL" if graph_matched or "retaliation" in itype.lower() else "HIGH",
                "case_id": cid,
                "entity_name": vname,
                "address": norm_loc if norm_loc else None,
                "apn": apn if apn else None,
                "proximity_cctv": cctv_prox,
                "evidence": f"Intake submission: {itype} | {summary_txt[:100]}"
            })
        log(f"Vector MUTUAL_AID: {len(mutual_cases)} cases ingested")
    else:
        summary["mutual_aid_leads_count"] = 0

    # 7. Scan datasets
    csv_leads = 0
    for pattern in ["tasklet_export/files/*.csv", "forensic/deliverables/*.csv", "data/*.csv"]:
        for csv_path in glob.glob(str(REPO_ROOT / pattern)):
            try:
                if os.path.getsize(csv_path) > 0:
                    csv_leads += 1
            except Exception:
                continue
    summary["csv_datasets_scanned"] = csv_leads
    summary["total_leads_generated"] = len(leads)
    
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    summary["elapsed"] = round(elapsed, 2)

    payload = {
        "generated_at": started.isoformat(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
        "engine": "auto_leads_correlation_v2",
        "version": "1.0-cloud-auto",
        "summary": summary,
        "graph_stats": {"nodes": len(nodes), "edges": len(edges)},
        "leads": leads,
        "next_run_hint": "Runs every 2h via GitHub Actions + continuous in Azure App Service if ENABLE_AUTO_CORRELATION=1"
    }

    try:
        LEADS_FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LEADS_FEED_PATH, "w", encoding="utf-8") as out:
            json.dump(payload, out, indent=2, ensure_ascii=False)
        log(f"Wrote live feed {LEADS_FEED_PATH} ({len(leads)} leads)")
    except Exception as e:
        log(f"ERROR writing leads_feed: {e}")

    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = started.strftime("%Y%m%d_%H%M%S")
        report_path = REPORTS_DIR / f"leads_{ts}.json"
        with open(report_path, "w", encoding="utf-8") as out:
            json.dump(payload, out, indent=2, ensure_ascii=False)
        log(f"Wrote report {report_path}")

        latest = REPORTS_DIR / "latest.json"
        with open(latest, "w", encoding="utf-8") as out:
            json.dump(payload, out, indent=2, ensure_ascii=False)

        reports = sorted([p for p in REPORTS_DIR.glob("leads_*.json")], key=lambda p: p.stat().st_mtime, reverse=True)
        for old in reports[50:]:
            try: old.unlink()
            except Exception: pass
    except Exception as e:
        log(f"ERROR writing report: {e}")

    log(f"=== COMPLETE {len(leads)} leads in {elapsed:.1f}s summary:{summary} ===")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", type=int, default=0, help="Loop forever every N seconds (0=single run)")
    args = parser.parse_args()
    if args.daemon and args.daemon > 0:
        log(f"Daemon mode every {args.daemon}s")
        while True:
            try:
                run_correlation()
            except Exception as e:
                log(f"DAEMON ERROR: {e}")
            time.sleep(args.daemon)
    else:
        run_correlation()
