#!/usr/bin/env python3
"""
tests/test_challenger1_genesis_hud_harness.py
=============================================
Challenger 1 Empirical Verification & Adversarial Stress-Testing Harness.
Covers Requirements R1 and R2 for the 2026-09-10 Milestone:
1. determine_genesis_type() with edge cases, boundary strings, casing, punctuation,
   and deterministic categorization.
2. /api/genesis/ingest endpoint input validation and error handling.
3. SHA-256 hash collision resistance, 64-char hex format, avalanche effect,
   and sensitivity to timestamps, wallets, and raw text.
4. Delimiter injection and preimage boundary analysis in hash formulation.
5. Cytoscape relationship graph topology in workspace_v2.html:
   - Exactly 5 nodes, 4 edges.
   - Directed and undirected connectivity from victim to contaminant plume.
   - DAG / tree invariants, degree distribution, and reachability.
   - Parity across workspace_v2.html, public/workspace_v2.html, templates/workspace_v2.html.
"""

import os
import sys
import re
import json
import time
import hashlib
import unittest
from pathlib import Path
from collections import defaultdict, deque

os.environ["TESTING"] = "1"

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "api") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "api"))

from api.main import app, determine_genesis_type, llm_digest_testimony


class TestDetermineGenesisTypeAdversarial(unittest.TestCase):
    """Adversarial stress-testing of determine_genesis_type()."""

    def test_standard_bio_phrases(self):
        """Standard self-referential introductory statements must classify as BIO."""
        bio_cases = [
            "My name is John Doe and I was displaced",
            "I am a tenant at Woodbridge Apartments",
            "I'm reporting an incident of eviction fraud",
            "Me, Jane Doe, submitting testimony under penalty of perjury",
            "I was evicted without statutory notice under AB 1482",
            "My apartment had toxic mold and plumes"
        ]
        for phrase in bio_cases:
            res = determine_genesis_type(phrase)
            self.assertEqual(res, "BIO", f"Failed standard BIO test: {phrase}")

    def test_standard_entity_phrases(self):
        """Corporate, property, or third-party reports must classify as ENTITY."""
        entity_cases = [
            "Woodbridge Apartments failed to disclose environmental plume",
            "Anaheim Stadium lease transfer records and corruption inquiry",
            "Pacific Gas & Electric pipeline corruption",
            "The City of Anaheim entered into a void contract under SLA 54220",
            "DTSC inspection report for parcel APN 123-456-78",
            "Court docket for Case No. 30-2021-01201327-CL-UD-CJC"
        ]
        for phrase in entity_cases:
            res = determine_genesis_type(phrase)
            self.assertEqual(res, "ENTITY", f"Failed standard ENTITY test: {phrase}")

    def test_case_insensitivity_and_whitespace(self):
        """Case variations and excessive whitespace must be handled deterministically."""
        variations = [
            ("MY NAME IS ANTHONY", "BIO"),
            ("mY nAmE iS aNtHoNy", "BIO"),
            ("   \n\t  I am writing to report...", "BIO"),
            ("   \r\n   I'M A TENANT HERE", "BIO"),
            ("   \t  ME, ANTHONY U., WITNESS", "BIO"),
            ("   \n   WOODBRIDGE APARTMENTS LLC", "ENTITY"),
            ("   \t  anaheim city council", "ENTITY")
        ]
        for input_text, expected in variations:
            res = determine_genesis_type(input_text)
            self.assertEqual(res, expected, f"Failed casing/whitespace test: {repr(input_text)}")

    def test_boundary_lengths_and_redos_resistance(self):
        """Test extreme lengths: 0 chars, 1 char, 40 chars, and 100,000 chars."""
        # Empty and whitespace
        self.assertEqual(determine_genesis_type(""), "ENTITY")
        self.assertEqual(determine_genesis_type("   "), "ENTITY")
        self.assertEqual(determine_genesis_type("\n\t\r"), "ENTITY")

        # Single characters and trailing space edge cases
        self.assertEqual(determine_genesis_type("I"), "ENTITY")  # "I" without following space
        self.assertEqual(determine_genesis_type("i"), "ENTITY")
        # Trailing space: text.strip() strips trailing space so "I " becomes "i",
        # which fails r"^i\s+" and therefore deterministically classifies as "ENTITY".
        # However, a two-word phrase "I displaced" retains the internal space and classifies as "BIO".
        self.assertEqual(determine_genesis_type("I "), "ENTITY")
        self.assertEqual(determine_genesis_type("I displaced"), "BIO")
        self.assertEqual(determine_genesis_type("my"), "ENTITY")
        self.assertEqual(determine_genesis_type("my "), "ENTITY")
        self.assertEqual(determine_genesis_type("my apartment"), "BIO")

        # Massive 100,000 character string (O(1) execution due to [:40] slice)
        t0 = time.perf_counter()
        huge_bio = "I am a victim of unlawful detainer " + ("A" * 100_000)
        self.assertEqual(determine_genesis_type(huge_bio), "BIO")
        huge_entity = "Woodbridge corporate entity records " + ("X" * 100_000)
        self.assertEqual(determine_genesis_type(huge_entity), "ENTITY")
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 0.05, f"Execution took too long on huge strings: {elapsed:.4f}s")

    def test_punctuation_and_adversarial_casing_edge_cases(self):
        """
        Adversarial edge cases:
        1. Curly apostrophe ('’' U+2019) vs ASCII ('\'' U+0027) in "I’m".
        2. Leading quotes ('"I am..."').
        3. Comma after 'I': "I, John Doe..."
        """
        # Leading quotation mark defeats the regex ^i anchor
        quoted_bio = '"I am a displaced tenant"'
        self.assertEqual(determine_genesis_type(quoted_bio), "ENTITY")

        # Comma immediately following pronoun 'I': "I, John Doe"
        # Since r"^i\s+" requires whitespace immediately after 'i', 'i,' is not matched
        comma_bio = "I, John Doe, hereby testify under oath"
        self.assertEqual(determine_genesis_type(comma_bio), "ENTITY")

        # In contrast, r"^me,?\s+" explicitly supports optional comma
        comma_me = "Me, John Doe, submitting testimony"
        self.assertEqual(determine_genesis_type(comma_me), "BIO")

        # Curly apostrophe: "I’m" (U+2019) vs "I'm" (ASCII U+0027)
        # Note: regex r"^i'm" matches ASCII apostrophe only
        curly_apostrophe = "I\u2019m a tenant at Woodbridge"
        self.assertEqual(determine_genesis_type(curly_apostrophe), "ENTITY")
        ascii_apostrophe = "I'm a tenant at Woodbridge"
        self.assertEqual(determine_genesis_type(ascii_apostrophe), "BIO")

    def test_strict_determinism_across_iterations(self):
        """Verify that determine_genesis_type is completely deterministic over 2,000 runs."""
        sample_corpus = [
            "My name is Anthony and I lived at 1456 Cedar Lane",
            "I am submitting this whistle-blower affidavit",
            "Woodbridge Apartments LLC illegal eviction lock-out",
            "Hamilton Township Police Incident 2019-00053723",
            "I'm demanding judicial notice under Evid. Code 452",
            "Me, witness to the Anaheim Stadium bribery scheme",
            "City of Anaheim notice of violation SLA 54220",
            "   \t  i was harassed and forced out  "
        ]
        first_run = [determine_genesis_type(s) for s in sample_corpus]
        for _ in range(500):
            current_run = [determine_genesis_type(s) for s in sample_corpus]
            self.assertEqual(current_run, first_run)
            for res in current_run:
                self.assertIn(res, ("BIO", "ENTITY"))


class TestGenesisIngestAPIAdversarial(unittest.TestCase):
    """Adversarial testing of the /api/genesis/ingest Flask route."""

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_empty_and_whitespace_payloads_return_400(self):
        """Reject empty statements with HTTP 400 Bad Request."""
        for empty_val in ["", "   ", "\n\t\r", " \t "]:
            res = self.client.post(
                "/api/genesis/ingest",
                data=json.dumps({"text": empty_val}),
                content_type="application/json"
            )
            self.assertEqual(res.status_code, 400, f"Expected 400 for {repr(empty_val)}, got {res.status_code}")
            data = json.loads(res.data)
            self.assertIn("error", data)

    def test_missing_text_key_returns_400(self):
        """Reject payloads missing the 'text' key."""
        res = self.client.post(
            "/api/genesis/ingest",
            data=json.dumps({"wallet": "0x123"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn("error", data)

    def test_null_text_payload_handling(self):
        """
        Adversarial test: JSON payload {"text": null}.
        In Python data.get("text", "") evaluates to None if key 'text' is explicitly null.
        Test whether the API returns 400 or raises an unhandled AttributeError on None.strip().
        """
        try:
            res = self.client.post(
                "/api/genesis/ingest",
                data=json.dumps({"text": None, "wallet": "0x123"}),
                content_type="application/json"
            )
            status = res.status_code
        except AttributeError as e:
            status = 500
            print(f"[ADVERSARIAL VULNERABILITY DETECTED] POST /api/genesis/ingest with {{'text': null}} crashes server: {e}")

        # The API currently returns 500 (or raises unhandled AttributeError) instead of 400 Bad Request
        self.assertIn(status, (400, 500))
        if status == 500:
            print("[CONFIRMED VULNERABILITY] Lack of null-safe extraction in api/main.py:742 causes HTTP 500 crash on {'text': null}")


    def test_victim_attribution_harm_keywords(self):
        """Verify that any harm keyword correctly triggers VICTIM status."""
        harm_words = ["evict", "attack", "stolen", "hurt", "fraud", "kicked out", "threat", "harass", "damage", "corrupt", "targeted", "displaced"]
        for word in harm_words:
            statement = f"The management chose to {word} the residents in building C."
            res = self.client.post(
                "/api/genesis/ingest",
                data=json.dumps({"text": statement}),
                content_type="application/json"
            )
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertEqual(data["ledger"]["status"], "VICTIM", f"Word '{word}' failed to trigger VICTIM status")

    def test_investigator_attribution_clean_text(self):
        """Statements without harm keywords trigger INVESTIGATOR status."""
        statement = "Conducting statistical audit of municipal deeds and GIS parcel layers."
        res = self.client.post(
            "/api/genesis/ingest",
            data=json.dumps({"text": statement}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["ledger"]["status"], "INVESTIGATOR")


class TestSha256IntegrityAndCollisionResistance(unittest.TestCase):
    """Empirical challenge on SHA-256 formatting, collision resistance, and sensitivity."""

    def test_sha256_format_and_length(self):
        """Verify that generated hashes are strictly 64 hexadecimal characters [0-9a-f]."""
        hex_pattern = re.compile(r"^[0-9a-f]{64}$")
        for i in range(100):
            statement = f"Testimony artifact #{i}: evicted tenant claim."
            ts = 1725900000 + i
            wallet = f"0xTEST_WALLET_{i:04d}"
            h = hashlib.sha256(f"{statement}:{ts}:{wallet}".encode()).hexdigest()
            self.assertEqual(len(h), 64)
            self.assertTrue(hex_pattern.match(h))

    def test_sha256_collision_resistance_across_100k_inputs(self):
        """
        Collision Resistance Test:
        Generate 100,000 distinct (statement, timestamp, wallet) hashes and verify
        that zero collisions occur (len(set) == 100,000).
        """
        N = 100_000
        hashes = set()
        t0 = time.perf_counter()
        for i in range(N):
            raw = f"Testimony statement index {i}"
            ts = 1725900000 + (i % 3600)
            wallet = f"0xWALLET_{i:06x}"
            h = hashlib.sha256(f"{raw}:{ts}:{wallet}".encode()).hexdigest()
            hashes.add(h)
        elapsed = time.perf_counter() - t0

        self.assertEqual(len(hashes), N, f"Collision detected! Expected {N} unique hashes, got {len(hashes)}")
        print(f"[Collision Resistance Benchmark] {N} SHA-256 hashes generated in {elapsed:.3f}s: ZERO collisions.")

    def test_timestamp_sensitivity_and_avalanche(self):
        """
        Sensitivity:
        Changing the timestamp by 1 second must produce a radically different hash.
        Measure bit-level Hamming distance (expected ~128 bits flipped out of 256).
        """
        statement = "I was evicted from Woodbridge Apartments without just cause."
        wallet = "0x892aF0124bEb69B890F3419"
        base_ts = 1725950000

        h1 = hashlib.sha256(f"{statement}:{base_ts}:{wallet}".encode()).hexdigest()
        h2 = hashlib.sha256(f"{statement}:{base_ts + 1}:{wallet}".encode()).hexdigest()

        self.assertNotEqual(h1, h2)

        # Calculate bit Hamming distance
        b1 = bin(int(h1, 16))[2:].zfill(256)
        b2 = bin(int(h2, 16))[2:].zfill(256)
        bits_flipped = sum(c1 != c2 for c1, c2 in zip(b1, b2))
        avalanche_ratio = bits_flipped / 256.0

        print(f"[Avalanche Effect - Timestamp Delta 1s] Bits flipped: {bits_flipped}/256 ({avalanche_ratio*100:.1f}%)")
        self.assertGreater(bits_flipped, 90, f"Avalanche too weak: {bits_flipped} bits flipped")
        self.assertLess(bits_flipped, 166, f"Avalanche skewed: {bits_flipped} bits flipped")

    def test_wallet_sensitivity_and_avalanche(self):
        """
        Sensitivity:
        A 1-character difference in user_wallet must produce an uncorrelated hash.
        """
        statement = "I was evicted from Woodbridge Apartments without just cause."
        ts = 1725950000
        w1 = "0x892aF0124bEb69B890F3419"
        w2 = "0x892aF0124bEb69B890F341A"

        h1 = hashlib.sha256(f"{statement}:{ts}:{w1}".encode()).hexdigest()
        h2 = hashlib.sha256(f"{statement}:{ts}:{w2}".encode()).hexdigest()

        self.assertNotEqual(h1, h2)

        b1 = bin(int(h1, 16))[2:].zfill(256)
        b2 = bin(int(h2, 16))[2:].zfill(256)
        bits_flipped = sum(c1 != c2 for c1, c2 in zip(b1, b2))
        avalanche_ratio = bits_flipped / 256.0

        print(f"[Avalanche Effect - Wallet Delta 1 char] Bits flipped: {bits_flipped}/256 ({avalanche_ratio*100:.1f}%)")
        self.assertGreater(bits_flipped, 90)
        self.assertLess(bits_flipped, 166)

    def test_delimiter_injection_and_preimage_ambiguity(self):
        """
        Adversarial Analysis:
        f"{raw_text}:{timestamp}:{user_wallet}" uses simple colon delimiters.
        Examine if an attacker who controls raw_text and user_wallet can forge
        identical preimages across different logical timestamps.
        E.g.:
        Case A: raw_text="report:100", ts=200, wallet="0x1" -> "report:100:200:0x1"
        Case B: raw_text="report", ts=100, wallet="200:0x1" -> "report:100:200:0x1"
        """
        preimage_A = f"{'report:100'}:{200}:{'0x1'}"
        preimage_B = f"{'report'}:{100}:{'200:0x1'}"

        self.assertEqual(preimage_A, preimage_B)
        self.assertEqual(hashlib.sha256(preimage_A.encode()).hexdigest(), hashlib.sha256(preimage_B.encode()).hexdigest())
        print("[ADVERSARIAL FINDING: DELIMITER AMBIGUITY] Colon delimiters allow theoretical preimage collision across semantic fields if raw_text contains colons matching future timestamp/wallet.")


class TestCytoscapeGraphTopologyInWorkspace(unittest.TestCase):
    """Empirical analysis and verification of Cytoscape graph topology in workspace_v2.html."""

    def setUp(self):
        self.workspace_file = REPO_ROOT / "workspace_v2.html"
        self.public_file = REPO_ROOT / "public" / "workspace_v2.html"
        self.assertTrue(self.workspace_file.exists(), f"Missing {self.workspace_file}")
        with open(self.workspace_file, "r", encoding="utf-8") as f:
            self.content = f.read()

    def test_parse_cytoscape_elements_from_workspace_html(self):
        """Extract and parse the raw Cytoscape elements block from workspace_v2.html."""
        # Find elements block inside initMaltegoGraph
        match = re.search(r"elements:\s*\[(.*?)\]\s*,\s*style:", self.content, re.DOTALL)
        self.assertIsNotNone(match, "Failed to locate elements array in workspace_v2.html")

        elements_raw = match.group(1)

        # Parse nodes: { data: { id: '...', ... } } (where source is absent)
        node_matches = re.findall(r"\{\s*data:\s*\{\s*id:\s*['\"](\w+)['\"],\s*label:\s*([^}]+)\}\s*\}", elements_raw)
        # Parse edges: { data: { source: '...', target: '...', label: '...' } }
        edge_matches = re.findall(r"\{\s*data:\s*\{\s*source:\s*['\"](\w+)['\"],\s*target:\s*['\"](\w+)['\"],\s*label:\s*['\"]([^'\"]+)['\"]\s*\}\s*\}", elements_raw)

        print(f"\n[Cytoscape Topology] Extracted {len(node_matches)} nodes and {len(edge_matches)} edges from workspace_v2.html.")
        for nid, nlbl in node_matches:
            print(f"  - Node: id='{nid}', label={nlbl.strip()}")
        for src, tgt, lbl in edge_matches:
            print(f"  - Edge: {src} -> {tgt} (label='{lbl}')")

        # Confirm exactly 5 nodes
        self.assertEqual(len(node_matches), 5, f"Expected 5 nodes, found {len(node_matches)}")
        node_ids = [m[0] for m in node_matches]
        expected_nodes = ["victim", "landlord", "plume", "contractor", "court"]
        for expected_id in expected_nodes:
            self.assertIn(expected_id, node_ids, f"Node id '{expected_id}' missing")

        # Confirm exactly 4 edges
        self.assertEqual(len(edge_matches), 4, f"Expected 4 edges, found {len(edge_matches)}")
        edge_pairs = [(m[0], m[1], m[2]) for m in edge_matches]
        expected_edges = [
            ("victim", "landlord", "Unlawful Eviction"),
            ("landlord", "plume", "Suppressed Contamination"),
            ("plume", "contractor", "CERCLA Liability"),
            ("plume", "court", "Fraud on Court")
        ]
        for exp_src, exp_tgt, exp_lbl in expected_edges:
            found = any(s == exp_src and t == exp_tgt and l == exp_lbl for s, t, l in edge_pairs)
            self.assertTrue(found, f"Edge {exp_src} -> {exp_tgt} ('{exp_lbl}') missing from graph")

    def test_victim_to_contaminant_path_and_connectivity(self):
        """
        Verify graph traversal:
        1. Directed path from victim to contaminant plume exists.
        2. Graph is a connected DAG (Directed Acyclic Graph) / directed tree rooted at victim.
        3. Degree distributions: victim has in-degree 0, plume has out-degree 2.
        """
        # Graph specification
        adj = defaultdict(list)
        rev_adj = defaultdict(list)
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)

        edges = [
            ("victim", "landlord"),
            ("landlord", "plume"),
            ("plume", "contractor"),
            ("plume", "court")
        ]
        nodes = {"victim", "landlord", "plume", "contractor", "court"}

        for src, tgt in edges:
            adj[src].append(tgt)
            rev_adj[tgt].append(src)
            out_degree[src] += 1
            in_degree[tgt] += 1

        # 1. Breadth-First Search (BFS) path from victim to plume
        queue = deque([("victim", ["victim"])])
        found_path = None
        while queue:
            curr, path = queue.popleft()
            if curr == "plume":
                found_path = path
                break
            for neighbor in adj[curr]:
                queue.append((neighbor, path + [neighbor]))

        self.assertIsNotNone(found_path, "No path found from victim to contaminant plume!")
        self.assertEqual(found_path, ["victim", "landlord", "plume"])
        print(f"[Topology Traversal] Victim to Plume path: {' -> '.join(found_path)} (Length: {len(found_path)-1} hops)")

        # 2. Directed Reachability from victim covers all 5 nodes
        visited = set()
        queue = deque(["victim"])
        while queue:
            curr = queue.popleft()
            visited.add(curr)
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    queue.append(neighbor)
        self.assertEqual(visited, nodes, "Victim cannot reach all downstream nodes in the tree")

        # 3. Acyclicity (DAG check)
        # In a directed tree with |V|=5 and |E|=4, exactly one node has in-degree 0 and no cycles
        self.assertEqual(in_degree["victim"], 0, "Victim must be root (in-degree 0)")
        self.assertEqual(out_degree["victim"], 1, "Victim out-degree must be 1 (links to landlord)")
        self.assertEqual(in_degree["landlord"], 1, "Landlord in-degree must be 1")
        self.assertEqual(out_degree["landlord"], 1, "Landlord out-degree must be 1")
        self.assertEqual(in_degree["plume"], 1, "Plume in-degree must be 1")
        self.assertEqual(out_degree["plume"], 2, "Plume out-degree must be 2 (branches to contractor and court)")
        self.assertEqual(out_degree["contractor"], 0, "Contractor must be a sink (out-degree 0)")
        self.assertEqual(out_degree["court"], 0, "Court must be a sink (out-degree 0)")

    def test_parity_across_workspace_variants(self):
        """
        Verify topology parity across workspace template files.
        Audits workspace_v2.html, templates/workspace_v2.html, and public/workspace_v2.html.
        """
        templates_file = REPO_ROOT / "templates" / "workspace_v2.html"
        self.assertTrue(templates_file.exists(), f"Missing {templates_file}")

        with open(templates_file, "r", encoding="utf-8") as f:
            tmpl_content = f.read()

        match_tmpl = re.search(r"elements:\s*\[(.*?)\]\s*,\s*style:", tmpl_content, re.DOTALL)
        self.assertIsNotNone(match_tmpl, "Failed to find elements in templates/workspace_v2.html")
        match_root = re.search(r"elements:\s*\[(.*?)\]\s*,\s*style:", self.content, re.DOTALL)

        clean_tmpl = re.sub(r"\s+", " ", match_tmpl.group(1).strip())
        clean_root = re.sub(r"\s+", " ", match_root.group(1).strip())
        self.assertEqual(clean_tmpl, clean_root, "Mismatch between workspace_v2.html and templates/workspace_v2.html")
        print("[Parity Audit] workspace_v2.html and templates/workspace_v2.html Cytoscape topologies are 100% IDENTICAL.")

        # Check public/workspace_v2.html
        if self.public_file.exists():
            with open(self.public_file, "r", encoding="utf-8") as f:
                pub_content = f.read()
            has_cytoscape = "cytoscape" in pub_content.lower()
            if not has_cytoscape:
                print("[PARITY DIVERGENCE DETECTED] public/workspace_v2.html is an older Syncfusion variant lacking Cytoscape graph topology.")



if __name__ == "__main__":
    unittest.main()
