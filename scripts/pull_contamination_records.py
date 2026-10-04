"""Contamination records pull — 17631 Cameron Ln / 17642 Beach Blvd, Huntington Beach.

Read-only GETs only. Uses the shared scienceskillscommon HttpClient
(rate limiting + retries + backoff) with a Windows fcntl shim, since the
stock skill file imports fcntl (Unix-only).

Targets:
  1. HB GIS ArcGIS REST — StormLayers / StormBroadcast / SewerBroadcast /
     Parcels service dirs + keyword-matched layer queries at the site envelope
  2. GeoTracker Phase I ESA PDF (fetch_bytes, long timeout)
  3. GeoTracker profile + ESI upload + HWTS + RCRAInfo + HB Accela
     (expected bot-blocked; status is recorded, never fatal)

Output: evidence/contamination_pull_manifest_<timestamp>.json
Lock files: %TEMP%/science-skills-<host>.lock
"""

import datetime
import json
import msvcrt
import os
import sys
import tempfile
import urllib.parse

SKILL_DIR = r"C:\OsintNeoAi\.agents\skills\scienceskillscommon"
EVIDENCE_DIR = r"C:\OsintNeoAi\evidence"
GEOTRACKER_DIR = os.path.join(EVIDENCE_DIR, "geotracker_edr")
sys.path.insert(0, SKILL_DIR)


# ---------------------------------------------------------------- Windows shim
class _FcntlShim:
    LOCK_EX = 1
    LOCK_UN = 2
    LOCK_SH = 4
    LOCK_NB = 8

    @staticmethod
    def flock(f, op):
        try:
            f.flush()
            f.seek(0)
            if op & _FcntlShim.LOCK_EX:
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
            else:
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass  # degrade to unlocked timestamp-gap limiting


sys.modules["fcntl"] = _FcntlShim

import http_client  # noqa: E402  (needs the shim above)

_orig_limiter_init = http_client._RateLimiter.__init__


def _patched_limiter_init(self, hostname, qps):
    _orig_limiter_init(self, hostname, qps)
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in hostname)
    self._lock_file = os.path.join(
        tempfile.gettempdir(), "%s-%s.lock" % (http_client.PROJECT_NAME, safe)
    )


http_client._RateLimiter.__init__ = _patched_limiter_init

# ---------------------------------------------------------------- constants
UA = "OsintNeoAi-research/1.0 (rate-limited public-records research)"
SITE_LON, SITE_LAT = -117.9902, 33.7081  # 17631 Cameron Ln hub
ENVELOPE = {
    "xmin": SITE_LON - 0.006,
    "ymin": SITE_LAT - 0.005,
    "xmax": SITE_LON + 0.006,
    "ymax": SITE_LAT + 0.005,
}
LAYER_KEYWORDS = ("inlet", "catch", "pipe", "conduit", "outfall", "drain", "sewer")

gis = http_client.HttpClient(
    "https://gis.huntingtonbeachca.gov/arcgis/rest/services/",
    qps=2,
    max_retries=2,
    timeout=25,
    user_agent=UA,
)
docs = http_client.HttpClient(
    "https://documents.geotracker.waterboards.ca.gov/",
    qps=1,
    max_retries=2,
    timeout=60,
    user_agent=UA,
)
web = http_client.HttpClient("https://geotracker.waterboards.ca.gov/", qps=1,
                             max_retries=2, timeout=25, user_agent=UA)

manifest = {"pulled_at": datetime.datetime.now().isoformat(), "entries": []}


def record(name, url, status, saved=None, detail="", n_features=None):
    entry = {"name": name, "url": url, "status": status}
    if saved:
        entry["saved"] = saved
    if detail:
        entry["detail"] = detail[:300]
    if n_features is not None:
        entry["features"] = n_features
    manifest["entries"].append(entry)
    print("%s -> %s %s" % (name, status, saved or detail))


def safe_json(client, name, url, save_name=None):
    try:
        data = client.fetch_json(url)
        path = None
        if save_name:
            path = os.path.join(EVIDENCE_DIR, save_name)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=1)
        record(name, url, "OK", saved=path,
               n_features=len(data.get("features", [])) if isinstance(data, dict) else None)
        return data
    except Exception as e:  # HttpError / URLError — record, don't crash
        record(name, url, getattr(e, "status", "ERROR"), detail=str(e))
        return None


# ------------------------------------------------------- 1. HB GIS services
def _host_reachable(host, port=443, timeout=8):
    import socket
    try:
        socket.create_connection((host, port), timeout=timeout).close()
        return True
    except OSError:
        return False


GIS_UP = _host_reachable("gis.huntingtonbeachca.gov")
service_layers = {}
if not GIS_UP:
    record("gis:host", "https://gis.huntingtonbeachca.gov/arcgis/rest/services/",
           "HOST_UNREACHABLE", detail="TCP 443 connect failed; skipping GIS pulls")
else:
    for svc in ["StormLayers/MapServer", "StormBroadcast/MapServer",
                "SewerBroadcast/MapServer", "Parcels/MapServer"]:
        url = "%s?f=json" % svc
        data = safe_json(gis, "gis:%s" % svc, url, save_name="gis_%s.json" % svc.split("/")[0])
        if isinstance(data, dict):
            service_layers[svc] = [
                (lyr.get("id"), lyr.get("name", ""))
                for lyr in data.get("layers", [])
                if any(k in lyr.get("name", "").lower() for k in LAYER_KEYWORDS)
            ] or [(lyr.get("id"), lyr.get("name", "")) for lyr in data.get("layers", [])[:3]]

geom = ",".join(str(ENVELOPE[k]) for k in ("xmin", "ymin", "xmax", "ymax"))
for svc, layers in service_layers.items():
    for lid, lname in layers:
        q = urllib.parse.urlencode({
            "where": "1=1",
            "geometry": geom,
            "geometryType": "esriGeometryEnvelope",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "false",
            "resultRecordCount": "100",
            "f": "json",
        })
        safe_json(gis, "gis:%s/%s" % (svc.split("/")[0], lname),
                  "%s/%s/query?%s" % (svc, lid, q),
                  save_name="gis_%s_L%s.json" % (svc.split("/")[0], lid))

# ------------------------------------------------------- 2. GeoTracker PDF
PDF_PATH = ("regulators/deliverable_documents/8203290641/"
            "T10000018579.20200318.Phase%20I%20Environmental%20Site%20Assessment.pdf")
try:
    pdf = docs.fetch_bytes(PDF_PATH)
    out = os.path.join(GEOTRACKER_DIR, "PhaseI_T10000018579_retry.pdf")
    with open(out, "wb") as f:
        f.write(pdf)
    record("geotracker:phase1-pdf", docs.base_url + PDF_PATH, "OK",
           saved=out, detail="%d bytes" % len(pdf))
except Exception as e:
    record("geotracker:phase1-pdf", docs.base_url + PDF_PATH,
           getattr(e, "status", "ERROR"), detail=str(e))

# ------------------------------------------------------- 3. Likely-blocked portals
safe_json(web, "geotracker:profile",
          "profile_report?global_id=T10000018579")
safe_json(web, "geotracker:esi-upload",
          "esi/uploads/geo_report/8599347770/T10000018579.PDF")
hwts = http_client.HttpClient("https://hwts.dtsc.ca.gov/", qps=1,
                              max_retries=2, timeout=25, user_agent=UA)
safe_json(hwts, "hwts:search", "search")
rcra = http_client.HttpClient("https://rcrainfo.epa.gov/", qps=1,
                              max_retries=2, timeout=25, user_agent=UA)
safe_json(rcra, "rcra:facility-search",
          "rcrainfoprod/action/public/public-site/facility-search")
accela = http_client.HttpClient("https://engage.huntingtonbeachca.gov/", qps=1,
                                max_retries=2, timeout=25, user_agent=UA)
safe_json(accela, "hb:accela-home",
          "CitizenAccess/Cap/CapHome.aspx?TabName=Home&module=Building")

# ------------------------------------------------------- manifest
os.makedirs(EVIDENCE_DIR, exist_ok=True)
mpath = os.path.join(
    EVIDENCE_DIR, "contamination_pull_manifest_%s.json"
    % datetime.datetime.now().strftime("%Y%m%d_%H%M"))
with open(mpath, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=1)
ok = sum(1 for e in manifest["entries"] if e["status"] == "OK")
print("DONE: %d/%d OK. Manifest: %s" % (ok, len(manifest["entries"]), mpath))
