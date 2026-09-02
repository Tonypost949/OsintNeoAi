#!/usr/bin/env python3
"""
tests/test_challenger1_empirical_harness.py
============================================
Challenger 1 Empirical Verification and Adversarial Stress-Testing Harness.
Covers Gate 3 and Requirement 2:
1. Spatial Fuzzing across 288 Caltrans D12 CCTV cameras (public and evidence geojsons).
2. Extreme Coordinate Boundary Fuzzing (polar, equator, antipodal, zero-distance, malformed).
3. Graph Integrity and Topology Analysis across 17,488 nodes and 18,712 edges.
4. CCTV Proximity Engine Execution and target_cctv_proximity.json Verification.
5. Multi-Vector Correlation Engine Execution and Leads Feed Verification across 6+ Vectors.
"""

import os
import sys
import json
import math
import time
import unittest
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.calculate_cctv_proximity import (
    haversine_miles,
    load_cctv_cameras,
    get_nearest_cctv,
    compute_proximity,
    TARGETS
)
import scripts.auto_leads_correlation_v2 as auto_leads

class TestChallenger1SpatialFuzzing(unittest.TestCase):
    """Empirical challenge and adversarial stress tests for spatial and CCTV datasets."""

    def setUp(self):
        self.public_cctv = REPO_ROOT / 'public' / 'caltrans_d12_cctv.geojson'
        self.evidence_cctv = REPO_ROOT / 'evidence' / 'caltrans_d12_cctv.geojson'

    def test_cctv_file_existence_and_parity(self):
        """Verify both CCTV GeoJSON files exist and contain identical feature counts."""
        self.assertTrue(self.public_cctv.exists(), f"Missing {self.public_cctv}")
        self.assertTrue(self.evidence_cctv.exists(), f"Missing {self.evidence_cctv}")

        with open(self.public_cctv, 'r', encoding='utf-8') as f:
            pub_data = json.load(f)
        with open(self.evidence_cctv, 'r', encoding='utf-8') as f:
            evi_data = json.load(f)

        pub_feats = pub_data.get('features', [])
        evi_feats = evi_data.get('features', [])
        self.assertEqual(len(pub_feats), 288, f"Expected 288 in public, got {len(pub_feats)}")
        self.assertEqual(len(evi_feats), 288, f"Expected 288 in evidence, got {len(evi_feats)}")

    def test_cctv_all_288_coordinates_validity(self):
        """Audit all 288 cameras: valid lat/lon, no NaNs, correct Orange County bounds."""
        cameras = load_cctv_cameras()
        self.assertEqual(len(cameras), 288, f"Expected 288 parsed cameras, got {len(cameras)}")

        for idx, cam in enumerate(cameras):
            cam_id = cam.get('id')
            lat = cam.get('lat')
            lon = cam.get('lon')
            loc = cam.get('location')

            self.assertTrue(cam_id, f"Camera index {idx} missing ID")
            self.assertIsInstance(lat, float, f"Camera {cam_id} lat is not float")
            self.assertIsInstance(lon, float, f"Camera {cam_id} lon is not float")
            self.assertFalse(math.isnan(lat) or math.isinf(lat), f"Camera {cam_id} invalid lat: {lat}")
            self.assertFalse(math.isnan(lon) or math.isinf(lon), f"Camera {cam_id} invalid lon: {lon}")

            # Orange County / Caltrans D12 bounding box validation:
            # Lat ~ 33.3 to 34.1, Lon ~ -118.5 to -117.4
            self.assertTrue(33.0 <= lat <= 34.5, f"Camera {cam_id} ({loc}) lat {lat} out of OC range")
            self.assertTrue(-118.5 <= lon <= -117.0, f"Camera {cam_id} ({loc}) lon {lon} out of OC range")

            # Validate streaming / image URL
            img_url = cam.get('image_url') or ''
            stream_url = cam.get('stream_url') or ''
            self.assertTrue(img_url.startswith('http') or stream_url.startswith('http'),
                            f"Camera {cam_id} lacks valid HTTP media URL")

    def test_haversine_exact_zero_distance(self):
        """Boundary test: Zero distance between identical coordinates."""
        test_points = [
            (33.6558, -117.8682),
            (33.7028, -117.9944),
            (0.0, 0.0),
            (90.0, 0.0),
            (-90.0, 0.0)
        ]
        for lat, lon in test_points:
            d = haversine_miles(lat, lon, lat, lon)
            self.assertEqual(d, 0.0, f"Zero distance failed for point ({lat}, {lon}): got {d}")

    def test_haversine_antipodal_extremes(self):
        """Boundary test: Antipodal points on globe must equal pi * R ~ 12,436.8 miles."""
        # North Pole to South Pole
        d_poles = haversine_miles(90.0, 0.0, -90.0, 0.0)
        self.assertAlmostEqual(d_poles, math.pi * 3958.8, delta=0.5)

        # Equator antipodal (0, 0) to (0, 180)
        d_eq = haversine_miles(0.0, 0.0, 0.0, 180.0)
        self.assertAlmostEqual(d_eq, math.pi * 3958.8, delta=0.5)

        # Arbitrary antipodal point: (lat, lon) to (-lat, lon + 180)
        lat, lon = 33.7042, -117.9893
        anti_lat, anti_lon = -33.7042, 62.0107
        d_arb = haversine_miles(lat, lon, anti_lat, anti_lon)
        self.assertAlmostEqual(d_arb, math.pi * 3958.8, delta=0.5)

    def test_haversine_equatorial_quadrant(self):
        """Boundary test: Quarter circumference on equator must equal (pi/2) * R ~ 6,218.4 miles."""
        d_quad = haversine_miles(0.0, 0.0, 0.0, 90.0)
        self.assertAlmostEqual(d_quad, (math.pi / 2.0) * 3958.8, delta=0.5)

    def test_haversine_malformed_and_edge_inputs(self):
        """Adversarial test: Non-numeric, None, NaN, and string inputs handled safely."""
        self.assertEqual(haversine_miles(None, 0.0, 0.0, 0.0), 9999.0)
        self.assertEqual(haversine_miles('invalid', 0.0, 0.0, 0.0), 9999.0)
        self.assertEqual(haversine_miles(float('nan'), 0.0, 0.0, 0.0), 9999.0)
        self.assertEqual(haversine_miles(float('inf'), 0.0, 0.0, 0.0), 9999.0)

    def test_nearest_cctv_boundary_queries(self):
        """Adversarial test: get_nearest_cctv at poles, equator, empty cameras, and exact locations."""
        cameras = load_cctv_cameras()

        # 1. Query at exact first camera position
        first_cam = cameras[0]
        nearest = get_nearest_cctv(first_cam['lat'], first_cam['lon'], k=4, cameras=cameras)
        self.assertEqual(len(nearest), 4)
        self.assertEqual(nearest[0]['id'], first_cam['id'])
        self.assertEqual(nearest[0]['distance_miles'], 0.0)

        # 2. Query at North Pole
        nearest_pole = get_nearest_cctv(90.0, 0.0, k=4, cameras=cameras)
        self.assertEqual(len(nearest_pole), 4)
        dists = [c['distance_miles'] for c in nearest_pole]
        self.assertEqual(dists, sorted(dists))
        self.assertTrue(all(d > 3800 for d in dists))

        # 3. Query with k > 288 (e.g. k=500)
        all_cams = get_nearest_cctv(33.7, -118.0, k=500, cameras=cameras)
        self.assertEqual(len(all_cams), 288)

        # 4. Query with k=0
        zero_k = get_nearest_cctv(33.7, -118.0, k=0, cameras=cameras)
        self.assertEqual(len(zero_k), 0)

        # 5. Query with empty cameras list
        empty_res = get_nearest_cctv(33.7, -118.0, k=4, cameras=[])
        self.assertEqual(empty_res, [])

        # 6. Query with None coordinates
        none_res = get_nearest_cctv(None, None, k=4, cameras=cameras)
        self.assertEqual(none_res, [])


class TestChallenger1GraphIntegrity(unittest.TestCase):
    """Empirical challenge and topological audit of nodes.json and edges.json."""

    def setUp(self):
        self.nodes_path = REPO_ROOT / 'nodes.json'
        self.edges_path = REPO_ROOT / 'edges.json'
        with open(self.nodes_path, 'r', encoding='utf-8') as f:
            self.nodes = json.load(f)
        with open(self.edges_path, 'r', encoding='utf-8') as f:
            self.edges = json.load(f)

    def test_node_and_edge_counts(self):
        """Verify exact node and edge cardinality in active knowledge graph."""
        self.assertEqual(len(self.nodes), 17488, f"Expected 17,488 nodes, got {len(self.nodes)}")
        self.assertEqual(len(self.edges), 18712, f"Expected 18,712 edges, got {len(self.edges)}")

    def test_node_id_uniqueness(self):
        """Verify 100% uniqueness of node IDs in nodes.json."""
        node_ids = set()
        duplicates = []
        for n in self.nodes:
            nid = n.get('id') if isinstance(n, dict) else None
            self.assertTrue(nid is not None, f"Node missing ID: {n}")
            if nid in node_ids:
                duplicates.append(nid)
            node_ids.add(nid)
        self.assertEqual(len(duplicates), 0, f"Found {len(duplicates)} duplicate node IDs: {duplicates[:10]}")
        self.assertEqual(len(node_ids), 17488)

    def test_node_type_distribution(self):
        """Analyze node label/type taxonomy distribution."""
        type_counts = Counter()
        for n in self.nodes:
            label = n.get('label') or n.get('type') or n.get('properties', {}).get('type', 'UNKNOWN')
            type_counts[label] += 1

        self.assertGreater(type_counts['ORGANIZATION'], 1000)
        self.assertGreater(type_counts['PERSON'], 1000)
        self.assertGreater(type_counts['PROPERTY'], 500)
        self.assertGreater(type_counts['ADDRESS'], 500)

    def test_edge_referential_integrity(self):
        """Audit edge references against node IDs, tracking dangling/orphan edges."""
        node_ids = {n.get('id') for n in self.nodes if isinstance(n, dict)}

        valid_edges = 0
        dangling_edges = []
        edge_types = Counter()

        for idx, e in enumerate(self.edges):
            if not isinstance(e, dict):
                continue
            etype = e.get('type') or e.get('label', 'UNKNOWN')
            edge_types[etype] += 1

            sid = e.get('source_id') or e.get('source')
            tid = e.get('target_id') or e.get('target')
            if isinstance(sid, dict): sid = sid.get('id')
            if isinstance(tid, dict): tid = tid.get('id')

            if sid in node_ids and tid in node_ids:
                valid_edges += 1
            else:
                dangling_edges.append((idx, etype, sid, tid))

        self.assertGreater(valid_edges, 15000, f"Too few valid edges: {valid_edges}")
        self.assertIn('RECEIVED_PPP', edge_types)
        self.assertIn('OWNS', edge_types)
        self.assertIn('OFFICER_OF', edge_types)
        self.assertIn('REGISTERED_AT', edge_types)

    def test_graph_self_loops_and_multi_edges(self):
        """Audit self-loops and multi-edges behavior."""
        self_loops = 0
        edge_pairs = Counter()

        for e in self.edges:
            if not isinstance(e, dict): continue
            sid = e.get('source_id') or e.get('source')
            tid = e.get('target_id') or e.get('target')
            if isinstance(sid, dict): sid = sid.get('id')
            if isinstance(tid, dict): tid = tid.get('id')

            if sid == tid:
                self_loops += 1
            edge_pairs[(sid, tid, e.get('type'))] += 1

        self.assertGreater(self_loops, 0, "Self-loops expected for entity event anchors")


class TestChallenger1ProximityAndCorrelationExecution(unittest.TestCase):
    """Empirical execution and output validation for calculate_cctv_proximity.py and auto_leads_correlation_v2.py."""

    def test_cctv_proximity_script_execution(self):
        """Execute calculate_cctv_proximity.py and verify output structure."""
        payload = compute_proximity()
        self.assertIsInstance(payload, dict)
        self.assertIn('targets_coverage', payload)
        self.assertIn('generated_at', payload)

        targets_cov = payload['targets_coverage']
        self.assertEqual(len(targets_cov), 4)

        for cov in targets_cov:
            tgt = cov['target']
            nearest = cov['nearest_cameras']
            radius = cov['coverage_radius_miles']

            self.assertIn(tgt['id'], ['DOVE_ST', 'CAMERON_LN', 'CENTER_AVE', 'BEACH_BLVD'])
            self.assertEqual(len(nearest), 4)
            self.assertEqual(radius, nearest[0]['distance_miles'])
            self.assertGreater(radius, 0.0)

            distances = [c['distance_miles'] for c in nearest]
            self.assertEqual(distances, sorted(distances))

        output_file = REPO_ROOT / 'evidence' / 'target_cctv_proximity.json'
        self.assertTrue(output_file.exists())

    def test_auto_leads_correlation_execution_and_vectors(self):
        """Execute auto_leads_correlation_v2.py and verify all 6+ lead vectors."""
        start_time = time.time()
        payload = auto_leads.run_correlation()
        runtime = time.time() - start_time

        self.assertLess(runtime, 5.0, f"Correlation engine exceeded 5s runtime: {runtime:.2f}s")
        self.assertIsInstance(payload, dict)
        self.assertIn('leads', payload)
        self.assertIn('summary', payload)
        self.assertIn('graph_stats', payload)

        leads = payload['leads']
        self.assertGreater(len(leads), 10, f"Expected >10 leads, got {len(leads)}")

        vectors_found = {l.get('vector') for l in leads}
        expected_vectors = {
            'PPP_PROPERTY_OVERLAP',
            'MULTI_ORG_PERSON',
            'ADDRESS_SHELL_CLUSTER',
            'HIGH_RISK_PPP',
            'LITIGATION_EXPOSURE',
        }
        for ev in expected_vectors:
            self.assertIn(ev, vectors_found, f"Missing lead vector: {ev}")

        spatial_leads = [l for l in leads if l.get('proximity_cctv')]
        self.assertGreater(len(spatial_leads), 0, "No leads enriched with CCTV proximity")

        feed_path = REPO_ROOT / 'data' / 'leads_feed.json'
        latest_report = REPO_ROOT / 'reports' / 'auto_leads' / 'latest.json'
        log_path = REPO_ROOT / 'logs' / 'correlation_runs.log'

        self.assertTrue(feed_path.exists(), "leads_feed.json missing")
        self.assertTrue(latest_report.exists(), "latest.json missing")
        self.assertTrue(log_path.exists(), "correlation_runs.log missing")

if __name__ == '__main__':
    unittest.main(verbosity=2)
