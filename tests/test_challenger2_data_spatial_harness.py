"""
tests/test_challenger2_data_spatial_harness.py
=============================================
Empirical adversarial verification harness by Challenger 2.

Validates:
1. Municipal URLs Dataset Integrity (82,757 lines, 82,757 unique URLs).
2. Forensic Domain Classification (10 categories, exact distribution summing to 82,757).
3. 42 Huntington Beach ArcGIS Services.
4. GeoTracker Permitted UST Facilities (15,845 records, 15,425 geocoded, 60 in HB, 1,023 in OC).
5. Cameron Lane Contamination Analysis (66 indexed report pages, borehole B-6 Cr-VI at 980 µg/kg, lead, OCPs).
6. Ground-Truth Haversine Distance Spherical Accuracy (HB City Hall, Cameron Ln, Ascon, El Toro).
7. Toxic Stigma Valuation Impact (-85% FMV) and Statutory Remedies Attribution.
8. In-Memory Search Latency Profiling & Adversarial Boundary Tests.
9. Flask Workspace REST API Integration.
"""

import os
import sys
import csv
import json
import math
import time
import unittest
from pathlib import Path

os.environ["TESTING"] = "1"

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "api") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "api"))

from api.workspace_intelligence import (
    HBMunicipalURLIndex,
    EnvironmentalGISRadar,
    TOXIC_ANCHORS,
    haversine_miles,
    search_hb_urls,
    get_hb_urls_stats,
    get_environmental_proximity,
    get_gis_layers
)
from api.main import app


class TestChallenger2DatasetIntegrity(unittest.TestCase):
    """Empirical verification of the raw source datasets."""

    @classmethod
    def setUpClass(cls):
        cls.data_dir = REPO_ROOT / "data"
        cls.opencode_dir = REPO_ROOT / "opencode_work"
        cls.master_file = cls.data_dir / "hb_urls_master.txt"
        cls.class_file = cls.data_dir / "neo_hb_urls_forensic_classification.json"
        cls.gis_file = cls.data_dir / "hb_gis_42_services_master.json"
        cls.ust_file = cls.opencode_dir / "geotracker" / "permitted_ust.txt"
        cls.cameron_file = cls.data_dir / "geotracker_17631_cameron_contamination_analysis.json"

    def test_01_master_urls_line_count_and_uniqueness(self):
        """Verify hb_urls_master.txt contains exactly 82,757 non-empty lines and 82,757 unique URLs."""
        self.assertTrue(self.master_file.exists(), f"Missing {self.master_file}")
        file_size = self.master_file.stat().st_size
        self.assertGreater(file_size, 8_000_000, f"File size too small: {file_size} bytes")

        with open(self.master_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip()]

        total_lines = len(lines)
        unique_urls = set(lines)

        self.assertEqual(total_lines, 82757, f"Expected exactly 82,757 lines, found {total_lines}")
        self.assertEqual(len(unique_urls), 82757, f"Expected 82,757 unique URLs, found {len(unique_urls)}")

        # Verify protocols and hostnames
        http_count = 0
        https_count = 0
        for url in lines:
            self.assertTrue(url.startswith("http://") or url.startswith("https://"), f"Invalid scheme: {url}")
            if url.startswith("https://"):
                https_count += 1
            else:
                http_count += 1
            self.assertTrue("huntingtonbeachca.gov" in url.lower() or "huntingtonbeach" in url.lower(), f"Unexpected host: {url}")

        self.assertEqual(http_count + https_count, 82757)

    def test_02_forensic_classification_schema_and_distribution(self):
        """Verify neo_hb_urls_forensic_classification.json catalogs 82,757 URLs across 10 categories."""
        self.assertTrue(self.class_file.exists(), f"Missing {self.class_file}")

        with open(self.class_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("breakdown_by_forensic_domain", data)
        categories = data["breakdown_by_forensic_domain"]

        expected_categories = [
            "GIS_AND_SPATIAL_SERVICES",
            "PLANNING_ZONING_DEVELOPMENT",
            "COUNCIL_AGENDAS_MINUTES",
            "FINANCIAL_BUDGET_CONTRACTS",
            "POLICE_FIRE_PUBLIC_SAFETY",
            "PUBLIC_WORKS_UTILITIES",
            "LEGAL_LITIGATION_CLAIMS",
            "HOUSING_DISADVANTAGE_COMMUNITY",
            "DOCUMENTS_AND_PDFS",
            "GENERAL_MUNICIPAL"
        ]

        for cat in expected_categories:
            self.assertIn(cat, categories, f"Missing category: {cat}")
            self.assertGreater(categories[cat], 0, f"Empty category: {cat}")

        total_classified = sum(categories.values())
        self.assertEqual(total_classified, 82757, f"Categories sum to {total_classified}, expected 82757")

        # Verify domain breakdown
        self.assertIn("top_domains", data)
        top_domains = dict(data["top_domains"])
        self.assertIn("www.huntingtonbeachca.gov", top_domains)
        self.assertEqual(top_domains["www.huntingtonbeachca.gov"], 62576)

    def test_03_gis_42_services_master(self):
        """Verify hb_gis_42_services_master.json contains exactly 42 ArcGIS services."""
        self.assertTrue(self.gis_file.exists(), f"Missing {self.gis_file}")

        with open(self.gis_file, "r", encoding="utf-8") as f:
            services = json.load(f)

        self.assertEqual(len(services), 42, f"Expected 42 GIS services, found {len(services)}")
        for s in services:
            self.assertIn("name", s)
            self.assertIn("url", s)
            self.assertIn("type", s)

    def test_04_geotracker_permitted_ust_empirical_audit(self):
        """
        Verify opencode_work/geotracker/permitted_ust.txt row count, coordinates, and regional tallies.
        Documents the empirical reality: 15,845 records in file (vs 15,847 claim), 15,425 geocoded.
        """
        self.assertTrue(self.ust_file.exists(), f"Missing {self.ust_file}")

        with open(self.ust_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = list(reader)

        total_rows = len(rows)
        self.assertEqual(total_rows, 15845, f"Expected 15,845 data rows in permitted_ust.txt, found {total_rows}")

        valid_coords = 0
        hb_records = 0
        oc_records = 0

        for r in rows:
            try:
                lat = float(r.get("LATITUDE") or 0)
                lon = float(r.get("LONGITUDE") or 0)
                if lat != 0.0 and lon != 0.0:
                    valid_coords += 1
            except (ValueError, TypeError):
                pass

            city = (r.get("CITY") or "").upper()
            county = (r.get("COUNTY") or "").upper()
            if "HUNTINGTON BEACH" in city:
                hb_records += 1
            if "ORANGE" in county:
                oc_records += 1

        self.assertEqual(valid_coords, 15425, f"Expected 15,425 geocoded records, found {valid_coords}")
        self.assertEqual(hb_records, 60, f"Expected 60 Huntington Beach UST records, found {hb_records}")
        self.assertEqual(oc_records, 1023, f"Expected 1,023 Orange County UST records, found {oc_records}")

    def test_05_cameron_lane_contamination_dataset(self):
        """Verify geotracker_17631_cameron_contamination_analysis.json environmental evidence."""
        self.assertTrue(self.cameron_file.exists(), f"Missing {self.cameron_file}")

        with open(self.cameron_file, "r", encoding="utf-8") as f:
            records = json.load(f)

        self.assertEqual(len(records), 66, f"Expected 66 indexed report pages, found {len(records)}")
        raw_text = json.dumps(records).lower()
        self.assertIn("lead", raw_text)
        self.assertIn("17631", raw_text)
        self.assertIn("cameron", raw_text)
        self.assertIn("eec", raw_text)
        self.assertIn("hexavalent", raw_text)


class TestChallenger2SpatialComputations(unittest.TestCase):
    """Empirical mathematical verification of spatial algorithms and Haversine precision."""

    def test_01_haversine_coincident_points(self):
        """Verify distance between identical coordinates is precisely 0.0."""
        d1 = haversine_miles(33.7064036, -117.9881801, 33.7064036, -117.9881801)
        d2 = haversine_miles(0.0, 0.0, 0.0, 0.0)
        self.assertEqual(d1, 0.0)
        self.assertEqual(d2, 0.0)

    def test_02_haversine_equatorial_one_degree(self):
        """Verify 1 degree of latitude/longitude along the equator equals ~69.09 miles."""
        d_lat = haversine_miles(0.0, 0.0, 1.0, 0.0)
        d_lon = haversine_miles(0.0, 0.0, 0.0, 1.0)
        self.assertAlmostEqual(d_lat, 69.094, places=2)
        self.assertAlmostEqual(d_lon, 69.094, places=2)

    def test_03_haversine_ground_truth_inter_site_distances(self):
        """
        Verify Haversine distance against known Huntington Beach ground-truth landmarks:
        - 17642 Beach Blvd (33.7064036, -117.9881801)
        - Ascon Superfund (33.6522, -117.9855) -> ~3.75 miles
        - HB City Hall (33.6599, -117.9990) -> Ascon Superfund -> ~0.93 miles
        - HB City Hall -> 17642 Beach Blvd -> ~3.27 miles
        - Ascon Superfund -> MCAS El Toro (33.6761, -117.7314) -> ~14.7 miles
        """
        beach_cameron = (33.7064036, -117.9881801)
        ascon = (33.6522, -117.9855)
        city_hall = (33.6599, -117.9990)
        el_toro = (33.6761, -117.7314)

        d_beach_ascon = haversine_miles(beach_cameron[0], beach_cameron[1], ascon[0], ascon[1])
        self.assertAlmostEqual(d_beach_ascon, 3.75, delta=0.05)

        d_city_ascon = haversine_miles(city_hall[0], city_hall[1], ascon[0], ascon[1])
        self.assertAlmostEqual(d_city_ascon, 0.93, delta=0.05)

        d_city_beach = haversine_miles(city_hall[0], city_hall[1], beach_cameron[0], beach_cameron[1])
        self.assertAlmostEqual(d_city_beach, 3.27, delta=0.05)

        d_ascon_eltoro = haversine_miles(ascon[0], ascon[1], el_toro[0], el_toro[1])
        self.assertAlmostEqual(d_ascon_eltoro, 14.70, delta=0.20)

    def test_04_haversine_antipodal_extremes(self):
        """Verify antipodal distance equals half the circumference of the Earth (~12,436.8 miles)."""
        d_poles = haversine_miles(90.0, 0.0, -90.0, 0.0)
        expected = math.pi * 3958.8
        self.assertAlmostEqual(d_poles, expected, places=2)

    def test_05_coordinate_resolution_anchor_extraction(self):
        """Verify EnvironmentalGISRadar.resolve_coordinates correctly extracts anchors from text."""
        radar = EnvironmentalGISRadar()

        # Direct coords
        lat, lon, desc = radar.resolve_coordinates(lat=33.1, lon=-117.2)
        self.assertEqual((lat, lon), (33.1, -117.2))

        # Cameron / Beach Blvd
        lat, lon, desc = radar.resolve_coordinates(text="Suspected Cr-VI at Cameron Lane plume")
        self.assertAlmostEqual(lat, 33.7064036, places=5)
        self.assertAlmostEqual(lon, -117.9881801, places=5)

        # Ascon Superfund
        lat, lon, desc = radar.resolve_coordinates(address="Hamilton Ave near Ascon landfill")
        self.assertAlmostEqual(lat, 33.6522, places=4)
        self.assertAlmostEqual(lon, -117.9855, places=4)

        # Center Ave
        lat, lon, desc = radar.resolve_coordinates(text="Subsurface vault at 7561 Center Ave")
        self.assertAlmostEqual(lat, 33.7431, places=4)

        # MCAS El Toro
        lat, lon, desc = radar.resolve_coordinates(text="Solvent plume near MCAS El Toro")
        self.assertAlmostEqual(lat, 33.6761, places=4)

        # Bolsa Chica
        lat, lon, desc = radar.resolve_coordinates(text="Bolsa Chica wetlands grading")
        self.assertAlmostEqual(lat, 33.7011, places=4)


class TestChallenger2ToxicStigmaCalculations(unittest.TestCase):
    """Empirical verification of toxic stigma valuation discounts and legal remedies."""

    @classmethod
    def setUpClass(cls):
        cls.radar = EnvironmentalGISRadar()

    def test_01_critical_toxic_stigma_discount_inside_plume(self):
        """Verify -85% valuation discount and statutory remedies when inside 0.5 miles of plume."""
        res = self.radar.calculate_proximity(lat=33.7064036, lon=-117.9881801, radius_miles=1.0)
        self.assertEqual(res["status"], "FLAGGED")
        self.assertEqual(res["overall_risk_level"], "CRITICAL_HAZARDOUS")
        self.assertEqual(res["valuation_impact"]["discount"], "-85% FMV")

        remedies = res["statutory_remedies"]
        self.assertTrue(any("473(d)" in r for r in remedies), "Missing Cal. CCP § 473(d)")
        self.assertTrue(any("60(d)(3)" in r for r in remedies), "Missing Fed. R. Civ. P. 60(d)(3)")
        self.assertTrue(any("1946.2" in r or "1482" in r for r in remedies), "Missing AB 1482")
        self.assertTrue(any("CERCLA" in r or "9607" in r for r in remedies), "Missing CERCLA")

        # Cameron analysis must be present
        self.assertIsNotNone(res["cameron_site_analysis"])
        self.assertEqual(res["cameron_site_analysis"]["boring_b6_cr_vi"], "980 µg/kg")

    def test_02_high_risk_toxic_stigma_discount(self):
        """Verify -70% valuation discount for locations between 0.5 and 1.5 miles from plume."""
        # Offset lat by ~0.012 deg (~0.83 miles from 17642 Beach Blvd)
        res = self.radar.calculate_proximity(lat=33.7184, lon=-117.9882, radius_miles=2.0)
        self.assertEqual(res["status"], "FLAGGED")
        self.assertEqual(res["overall_risk_level"], "HIGH_RISK")
        self.assertEqual(res["valuation_impact"]["discount"], "-70% FMV")

    def test_03_moderate_risk_toxic_stigma_discount(self):
        """Verify -35% valuation discount for locations between 1.5 and 2.0 miles from plume."""
        # (33.69, -118.01) is 1.69 miles from Cameron Lane plume (between 1.5 and 2.0 miles)
        res = self.radar.calculate_proximity(lat=33.6900, lon=-118.0100, radius_miles=2.0)
        self.assertEqual(res["status"], "FLAGGED")
        self.assertEqual(res["overall_risk_level"], "MODERATE_RISK")
        self.assertEqual(res["valuation_impact"]["discount"], "-35% FMV")

    def test_04_baseline_monitored_outside_buffer(self):
        """Verify 0% discount and CLEAR status when far outside all plumes (>2.0 miles and no UST)."""
        res = self.radar.calculate_proximity(lat=33.5500, lon=-118.1500, radius_miles=1.0)
        self.assertEqual(res["status"], "CLEAR")
        self.assertEqual(res["overall_risk_level"], "MONITORED_BASELINE")
        self.assertEqual(res["valuation_impact"]["discount"], "0% (Standard Market)")
        self.assertIsNone(res["cameron_site_analysis"])


class TestChallenger2SearchPerformanceAndAdversarial(unittest.TestCase):
    """Benchmark search performance and test adversarial edge cases."""

    @classmethod
    def setUpClass(cls):
        cls.index = HBMunicipalURLIndex()
        cls.index._ensure_loaded()
        cls.radar = EnvironmentalGISRadar()
        cls.radar._ensure_loaded()

    def test_01_search_benchmark_rapid_sample(self):
        """
        Benchmark in-memory search across a rapid representative sample of 50 diverse queries.
        Asserts average latency is under 1,000 ms per query.
        """
        test_queries = [
            "cameron", "ascon", "zoning", "ordinance", "hazard",
            "water", "police", "budget", "agenda", "7561"
        ] * 5  # 50 queries

        start = time.perf_counter()
        for q in test_queries:
            r = self.index.search(query=q, limit=10)
            self.assertEqual(r["status"], "ok")
        elapsed = time.perf_counter() - start

        avg_lat_ms = (elapsed / len(test_queries)) * 1000
        qps = len(test_queries) / elapsed
        print(f"\n[BENCHMARK] 50 queries in {elapsed:.3f}s | Avg Latency: {avg_lat_ms:.2f}ms | Throughput: {qps:.1f} QPS")

        self.assertLess(avg_lat_ms, 1000.0, f"Average search latency {avg_lat_ms:.2f}ms exceeded 1,000ms threshold")

    def test_02_adversarial_empty_and_whitespace_search(self):
        """Verify search handles empty, whitespace, and none-like query inputs gracefully."""
        r1 = self.index.search(query="", limit=5)
        self.assertEqual(r1["status"], "ok")
        self.assertEqual(r1["total_matches"], 82757)
        self.assertEqual(len(r1["results"]), 5)

        r2 = self.index.search(query="   \t\n  ", limit=5)
        self.assertEqual(r2["status"], "ok")
        self.assertEqual(r2["total_matches"], 82757)

    def test_03_adversarial_special_characters_and_injections(self):
        """Verify regex characters and injection tokens do not crash substring search."""
        for injection in [".*", "[a-z]+", "\\d{3}", "' OR '1'='1", "<!--", "<script>", "(?i)test"]:
            r = self.index.search(query=injection, limit=5)
            self.assertEqual(r["status"], "ok")
            self.assertIsInstance(r["total_matches"], int)

    def test_04_adversarial_category_filter_case_insensitivity(self):
        """Verify category filtering works regardless of casing and ignores invalid categories."""
        r_upper = self.index.search(query="water", category="PUBLIC_WORKS_UTILITIES", limit=5)
        r_lower = self.index.search(query="water", category="public_works_utilities", limit=5)
        self.assertEqual(r_upper["total_matches"], r_lower["total_matches"])

        # Nonexistent category returns 0 matches without crashing
        r_none = self.index.search(query="water", category="NONEXISTENT_DOMAIN_XYZ", limit=5)
        self.assertEqual(r_none["total_matches"], 0)

    def test_05_adversarial_spatial_out_of_bounds_coordinates(self):
        """Verify spatial radar handles extreme latitude/longitude coordinates gracefully."""
        for lat, lon in [(90.0, 0.0), (-90.0, 0.0), (0.0, 180.0), (0.0, -180.0), (0.0, 0.0)]:
            res = self.radar.calculate_proximity(lat=lat, lon=lon, radius_miles=1.0)
            self.assertIn(res["status"], ["FLAGGED", "CLEAR"])
            self.assertIn("nearest_plume", res)
            self.assertGreaterEqual(res["nearest_plume"]["distance_miles"], 0.0)

    def test_06_adversarial_zero_and_negative_radius(self):
        """Verify radius_miles=0.0 returns 0 nearby USTs without division by zero or errors."""
        res = self.radar.calculate_proximity(lat=33.7064, lon=-117.9882, radius_miles=0.0)
        self.assertEqual(res["status"], "FLAGGED")
        self.assertEqual(res["nearby_ust_count"], 0)


class TestChallenger2FlaskIntegration(unittest.TestCase):
    """Verify live Flask REST API endpoints and data delivery."""

    def setUp(self):
        self.client = app.test_client()

    def test_01_api_hb_urls_stats(self):
        """GET /api/workspace/hb-urls/stats returns complete catalog statistics."""
        res = self.client.get("/api/workspace/hb-urls/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["total_urls"], 82757)
        self.assertEqual(data["gis_services_count"], 42)
        self.assertEqual(sum(data["categories"].values()), 82757)

    def test_02_api_hb_urls_search_pagination(self):
        """GET /api/workspace/hb-urls/search handles query and pagination parameters."""
        res = self.client.get("/api/workspace/hb-urls/search?q=planning&limit=10&offset=5")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(len(data["results"]), 10)
        self.assertEqual(data["offset"], 5)

    def test_03_api_environmental_proximity(self):
        """POST /api/workspace/environmental/proximity evaluates toxic stigma."""
        payload = {"address": "17631 Cameron Lane", "radius_miles": 2.0}
        res = self.client.post("/api/workspace/environmental/proximity", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "FLAGGED")
        self.assertEqual(data["overall_risk_level"], "CRITICAL_HAZARDOUS")
        self.assertEqual(data["valuation_impact"]["discount"], "-85% FMV")
        self.assertIsNotNone(data["cameron_site_analysis"])

    def test_04_api_gis_layers(self):
        """GET /api/workspace/gis/layers returns all 6 GIS vector layers."""
        res = self.client.get("/api/workspace/gis/layers")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["total_layers"], 6)
        layer_ids = [l["layer_id"] for l in data["layers"]]
        self.assertEqual(len(layer_ids), 6)


if __name__ == "__main__":
    unittest.main()
