"""
tests/test_workspace_intelligence.py
====================================
Unit and integration test suite for HBMunicipalURLIndex (82,757 URLs),
EnvironmentalGISRadar, Flask API endpoints in api/main.py,
and template parity between workspace_v2.html and templates/workspace_v2.html.
"""

import os
import sys
import json
import re
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
    search_hb_urls,
    get_hb_urls_stats,
    get_environmental_proximity,
    get_gis_layers,
    haversine_miles
)
from api.main import app


class TestHBMunicipalURLIndex(unittest.TestCase):
    """Test suite for HBMunicipalURLIndex and 82,757 municipal URLs."""

    @classmethod
    def setUpClass(cls):
        cls.index = HBMunicipalURLIndex()

    def test_get_stats_and_counts(self):
        """Verify total URL count and forensic domain breakdown."""
        stats = self.index.get_stats()
        self.assertEqual(stats["status"], "ok")
        self.assertGreaterEqual(stats["total_urls"], 82757)
        self.assertEqual(stats["gis_services_count"], 42)
        self.assertIn("categories", stats)
        cats = stats["categories"]
        self.assertIn("PLANNING_ZONING_DEVELOPMENT", cats)
        self.assertIn("COUNCIL_AGENDAS_MINUTES", cats)
        self.assertIn("DOCUMENTS_AND_PDFS", cats)
        self.assertIn("GENERAL_MUNICIPAL", cats)

    def test_search_substring(self):
        """Verify case-insensitive substring search in 82,757 URLs."""
        res = self.index.search(query="planning", limit=10)
        self.assertEqual(res["status"], "ok")
        self.assertGreater(res["total_matches"], 100)
        self.assertLessEqual(len(res["results"]), 10)
        for r in res["results"]:
            self.assertIn("planning", r["url"].lower())

    def test_search_category_filter(self):
        """Verify filtering by forensic category."""
        res = self.index.search(query="water", category="PUBLIC_WORKS_UTILITIES", limit=10)
        self.assertEqual(res["status"], "ok")
        self.assertGreater(res["total_matches"], 0)
        for r in res["results"]:
            self.assertEqual(r["category"], "PUBLIC_WORKS_UTILITIES")

    def test_search_pagination(self):
        """Verify offset and limit pagination."""
        res1 = self.index.search(query="agenda", limit=5, offset=0)
        res2 = self.index.search(query="agenda", limit=5, offset=5)
        self.assertEqual(len(res1["results"]), 5)
        self.assertEqual(len(res2["results"]), 5)
        urls1 = [x["url"] for x in res1["results"]]
        urls2 = [x["url"] for x in res2["results"]]
        self.assertNotEqual(urls1, urls2)

    def test_cross_reference_entities(self):
        """Verify entity cross-referencing against municipal records."""
        matches = self.index.cross_reference_entities(["Woodbridge", "Planning", "Council"], limit_per_entity=3)
        self.assertIn("Planning", matches)
        self.assertGreater(len(matches["Planning"]), 0)


class TestEnvironmentalGISRadar(unittest.TestCase):
    """Test suite for EnvironmentalGISRadar and spatial proximity calculations."""

    @classmethod
    def setUpClass(cls):
        cls.radar = EnvironmentalGISRadar()

    def test_haversine_accuracy(self):
        """Verify Haversine distance computation on known coordinates."""
        # 17642 Beach Blvd to Ascon Superfund (~3.75 miles)
        d = haversine_miles(33.7064, -117.9882, 33.6522, -117.9855)
        self.assertAlmostEqual(d, 3.75, delta=0.5)

    def test_proximity_beach_blvd_focal_point(self):
        """Verify Beach Blvd / Cameron Ln toxic plume intercept."""
        res = self.radar.calculate_proximity(address="17642 Beach Blvd", radius_miles=2.0)
        self.assertEqual(res["status"], "FLAGGED")
        self.assertEqual(res["overall_risk_level"], "CRITICAL_HAZARDOUS")
        self.assertIn("valuation_impact", res)
        self.assertEqual(res["valuation_impact"]["discount"], "-85% FMV")

        # Nearest plume should be Beach/Cameron
        np = res.get("nearest_plume")
        self.assertIsNotNone(np)
        self.assertIn("17642 Beach Blvd", np["name"])
        self.assertLessEqual(np["distance_miles"], 0.1)

        # Cameron analysis should be injected
        self.assertIsNotNone(res.get("cameron_site_analysis"))
        self.assertEqual(res["cameron_site_analysis"]["boring_b6_cr_vi"], "980 µg/kg")

    def test_proximity_ascon_superfund(self):
        """Verify Ascon Superfund detection via coordinates."""
        res = self.radar.calculate_proximity(lat=33.6522, lon=-117.9855, radius_miles=1.0)
        self.assertEqual(res["status"], "FLAGGED")
        self.assertEqual(res["overall_risk_level"], "CRITICAL_HAZARDOUS")
        np = res.get("nearest_plume")
        self.assertIn("Ascon", np["name"])
        self.assertAlmostEqual(np["distance_miles"], 0.0, delta=0.01)

    def test_nearby_ust_facilities(self):
        """Verify retrieval of nearby GeoTracker permitted UST facilities."""
        res = self.radar.calculate_proximity(lat=33.7064, lon=-117.9882, radius_miles=2.0)
        self.assertIn("nearby_ust_count", res)
        self.assertGreater(res["nearby_ust_count"], 0)
        usts = res["nearby_ust_facilities"]
        self.assertGreater(len(usts), 0)
        # Verify distance ordering
        distances = [u["distance_miles"] for u in usts]
        self.assertEqual(distances, sorted(distances))

    def test_gis_layers_metadata(self):
        """Verify GIS layers catalog."""
        layers = self.radar.get_gis_layers()
        self.assertEqual(layers["status"], "ok")
        self.assertEqual(layers["total_layers"], 6)
        layer_ids = [l["layer_id"] for l in layers["layers"]]
        self.assertIn("hb_parcels", layer_ids)
        self.assertIn("hb_surface_flow", layer_ids)
        self.assertIn("hb_planning", layer_ids)
        self.assertIn("caltrans_cctv", layer_ids)
        self.assertIn("geotracker_permitted_ust", layer_ids)
        self.assertIn("toxic_plume_vectors", layer_ids)


class TestFlaskWorkspaceEndpoints(unittest.TestCase):
    """Test suite for workspace and GIS REST endpoints in api/main.py."""

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_endpoint_hb_urls_stats(self):
        """Test GET /api/workspace/hb-urls/stats."""
        res = self.client.get("/api/workspace/hb-urls/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertGreaterEqual(data["total_urls"], 82757)
        self.assertEqual(data["gis_services_count"], 42)

    def test_endpoint_hb_urls_search_get(self):
        """Test GET /api/workspace/hb-urls/search."""
        res = self.client.get("/api/workspace/hb-urls/search?q=planning&limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertGreater(data["total_matches"], 0)
        self.assertEqual(len(data["results"]), 5)

    def test_endpoint_hb_urls_search_post(self):
        """Test POST /api/workspace/hb-urls/search."""
        payload = {"q": "agenda", "category": "COUNCIL_AGENDAS_MINUTES", "limit": 4}
        res = self.client.post("/api/workspace/hb-urls/search", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertLessEqual(len(data["results"]), 4)
        for r in data["results"]:
            self.assertEqual(r["category"], "COUNCIL_AGENDAS_MINUTES")

    def test_endpoint_environmental_proximity_get(self):
        """Test GET /api/workspace/environmental/proximity."""
        res = self.client.get("/api/workspace/environmental/proximity?lat=33.7064&lon=-117.9882&radius_miles=2.0")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "FLAGGED")
        self.assertIn("valuation_impact", data)
        self.assertEqual(data["valuation_impact"]["discount"], "-85% FMV")

    def test_endpoint_environmental_proximity_post(self):
        """Test POST /api/workspace/environmental/proximity."""
        payload = {"address": "17642 Beach Blvd", "radius_miles": 1.5}
        res = self.client.post("/api/workspace/environmental/proximity", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "FLAGGED")
        self.assertIsNotNone(data["nearest_plume"])

    def test_endpoint_gis_layers(self):
        """Test GET /api/workspace/gis/layers."""
        res = self.client.get("/api/workspace/gis/layers")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["total_layers"], 6)

    def test_genesis_ingest_null_safety(self):
        """Test null-safety fix at api/main.py:742 with {'text': None}."""
        res = self.client.post("/api/genesis/ingest", json={"text": None})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)

    def test_genesis_ingest_enrichment(self):
        """Test that /api/genesis/ingest returns municipal_matches and environmental_proximity."""
        payload = {
            "text": "I was evicted by Woodbridge Apartments security while investigating the Beach Blvd toxic plume.",
            "wallet": "0xVICTIM_INTEL_ADDR"
        }
        res = self.client.post("/api/genesis/ingest", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("municipal_matches", data)
        self.assertIn("environmental_proximity", data)
        self.assertEqual(data["environmental_plume_intercept"]["status"], "FLAGGED")
        self.assertEqual(data["environmental_plume_intercept"]["valuation_discount"], "-85% FMV")
        self.assertIn("473(d)", data["environmental_plume_intercept"]["statutory_remedy"])


class TestWorkspaceTemplateParity(unittest.TestCase):
    """Test suite for workspace template parity and Cytoscape topology."""

    def test_template_parity_exact(self):
        """Verify workspace_v2.html and templates/workspace_v2.html are 100% identical."""
        w_file = REPO_ROOT / "workspace_v2.html"
        t_file = REPO_ROOT / "templates" / "workspace_v2.html"
        self.assertTrue(w_file.exists(), "Missing workspace_v2.html")
        self.assertTrue(t_file.exists(), "Missing templates/workspace_v2.html")
        w_content = w_file.read_text(encoding="utf-8")
        t_content = t_file.read_text(encoding="utf-8")
        self.assertEqual(w_content, t_content, "workspace_v2.html and templates/workspace_v2.html must be 100% byte-for-byte identical")

    def test_cytoscape_5_nodes_topology_preservation(self):
        """Verify that initMaltegoGraph preserves the exact 5 nodes and 4 edges."""
        w_file = REPO_ROOT / "workspace_v2.html"
        content = w_file.read_text(encoding="utf-8")
        match = re.search(r"elements:\s*\[(.*?)\]\s*,\s*style:", content, re.DOTALL)
        self.assertIsNotNone(match, "Failed to find elements array in workspace_v2.html")
        elements_raw = match.group(1)

        node_matches = re.findall(r"\{\s*data:\s*\{\s*id:\s*['\"](\w+)['\"],\s*label:\s*([^}]+)\}\s*\}", elements_raw)
        edge_matches = re.findall(r"\{\s*data:\s*\{\s*source:\s*['\"](\w+)['\"],\s*target:\s*['\"](\w+)['\"],\s*label:\s*['\"]([^'\"]+)['\"]\s*\}\s*\}", elements_raw)

        self.assertEqual(len(node_matches), 5, f"Expected exactly 5 initial nodes, found {len(node_matches)}")
        self.assertEqual(len(edge_matches), 4, f"Expected exactly 4 initial edges, found {len(edge_matches)}")

        node_ids = [m[0] for m in node_matches]
        for exp in ["victim", "landlord", "plume", "contractor", "court"]:
            self.assertIn(exp, node_ids)

    def test_presence_of_municipal_and_radar_controls(self):
        """Verify that #hb-urls-pane and environmental radar controls exist in template."""
        w_file = REPO_ROOT / "workspace_v2.html"
        content = w_file.read_text(encoding="utf-8")
        self.assertIn('id="hb-urls-pane"', content)
        self.assertIn('id="url-search-input"', content)
        self.assertIn('id="url-results-container"', content)
        self.assertIn('id="plume-metrics"', content)
        self.assertIn('generateMotion473d()', content)


if __name__ == "__main__":
    unittest.main()
