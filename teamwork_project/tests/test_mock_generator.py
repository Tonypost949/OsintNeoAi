"""
Unit Test Suite for Synthetic OSINT Dataset Generator (`src/engine/mock_generator.py`).
"""
import csv
import json
import sys
from pathlib import Path
import pytest

from src.engine.mock_generator import generate_synthetic_osint_dataset, main


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provides a temporary directory path for test datasets."""
    return tmp_path / "mock_data"


def test_generate_synthetic_osint_dataset_creates_files(temp_output_dir):
    """Verify that generate_synthetic_osint_dataset creates all 6 expected files."""
    file_map = generate_synthetic_osint_dataset(output_dir=temp_output_dir, num_nodes=100, num_hubs=3, seed=42)
    
    assert len(file_map) == 6
    for key, file_path in file_map.items():
        assert file_path.exists(), f"Expected generated file missing: {key} at {file_path}"
        assert file_path.stat().st_size > 0, f"Generated file is empty: {file_path}"


def test_csv_schemas_and_rows(temp_output_dir):
    """Validate CSV headers and non-empty rows for all generated CSV files."""
    file_map = generate_synthetic_osint_dataset(output_dir=temp_output_dir, num_nodes=200, num_hubs=3, seed=42)

    # 1. Nevada SOS
    with open(file_map["nevada_sos"], "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        assert "Entity_ID" in headers
        assert "Business_Name" in headers
        assert "Registered_Agent_Address" in headers
        rows = list(reader)
        assert len(rows) >= 20

    # 2. SBA PPP Loans
    with open(file_map["sba_ppp_loans"], "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        assert "LoanNumber" in headers
        assert "BorrowerName" in headers
        assert "CurrentApprovalAmount" in headers
        rows = list(reader)
        assert len(rows) >= 20

    # 3. Property Records
    with open(file_map["property_records"], "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        assert "Parcel_ID" in headers
        assert "Property_Address" in headers
        assert "Owner_Name" in headers
        rows = list(reader)
        assert len(rows) >= 20

    # 4. IRS 990
    with open(file_map["irs_990"], "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        assert "EIN" in headers
        assert "Organization_Name" in headers
        assert "Principal_Officer" in headers
        rows = list(reader)
        assert len(rows) >= 10


def test_json_graph_structure(temp_output_dir):
    """Validate structure and fields of nodes.json and edges.json."""
    file_map = generate_synthetic_osint_dataset(output_dir=temp_output_dir, num_nodes=100, num_hubs=2, seed=42)

    with open(file_map["nodes"], "r", encoding="utf-8") as f:
        nodes = json.load(f)
        assert isinstance(nodes, list)
        assert len(nodes) > 0
        node = nodes[0]
        assert "node_id" in node
        assert "node_type" in node
        assert "label" in node

    with open(file_map["edges"], "r", encoding="utf-8") as f:
        edges = json.load(f)
        assert isinstance(edges, list)
        assert len(edges) > 0
        edge = edges[0]
        assert "edge_id" in edge
        assert "source_id" in edge
        assert "target_id" in edge
        assert "edge_type" in edge


def test_shared_address_hubs(temp_output_dir):
    """Validate that multiple entities share high-degree address hubs."""
    file_map = generate_synthetic_osint_dataset(output_dir=temp_output_dir, num_nodes=400, num_hubs=2, seed=42)

    address_counts = {}
    with open(file_map["nevada_sos"], "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = row["Registered_Agent_Address"]
            address_counts[addr] = address_counts.get(addr, 0) + 1

    # At least one address hub must be shared by multiple entities
    max_shared = max(address_counts.values()) if address_counts else 0
    assert max_shared >= 3, f"Expected high-degree address hub with >= 3 entities, got max {max_shared}"


def test_deterministic_reproducibility(temp_output_dir):
    """Verify that running generator with identical seeds produces identical output files."""
    dir_a = temp_output_dir / "run_a"
    dir_b = temp_output_dir / "run_b"

    map_a = generate_synthetic_osint_dataset(output_dir=dir_a, num_nodes=100, num_hubs=3, seed=12345)
    map_b = generate_synthetic_osint_dataset(output_dir=dir_b, num_nodes=100, num_hubs=3, seed=12345)

    with open(map_a["nevada_sos"], "r", encoding="utf-8") as fa, open(map_b["nevada_sos"], "r", encoding="utf-8") as fb:
        assert fa.read() == fb.read()

    with open(map_a["nodes"], "r", encoding="utf-8") as fa, open(map_b["nodes"], "r", encoding="utf-8") as fb:
        assert fa.read() == fb.read()


def test_cli_interface(temp_output_dir, monkeypatch):
    """Test command-line main() execution."""
    cli_dir = temp_output_dir / "cli_run"
    test_args = ["mock_generator", "--output-dir", str(cli_dir), "--num-nodes", "50", "--seed", "42"]
    monkeypatch.setattr(sys, "argv", test_args)

    main()

    assert (cli_dir / "nevada_sos.csv").exists()
    assert (cli_dir / "nodes.json").exists()
