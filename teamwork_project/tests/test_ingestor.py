"""
Unit Test Suite for OSINT Data Ingestion Engine (src/engine/ingestor.py).
"""
import json
import pytest
from pathlib import Path
from src.engine.ingestor import (
    parse_nodes_json,
    parse_edges_json,
    parse_ppp_loans_csv,
    parse_sos_records_csv,
    parse_property_records_csv,
    IngestionResult,
    _clean_numeric
)


@pytest.fixture
def sample_nodes_json(tmp_path):
    file_path = tmp_path / "nodes.json"
    data = [
        {
            "id": "ACME CORP LLC",
            "label": "ORGANIZATION",
            "properties": {"name": "ACME CORP LLC"}
        },
        {
            "id": "APN-123-456",
            "label": "PROPERTY",
            "properties": {"apn": "APN-123-456", "assessed_value": "450000"}
        },
        {
            "id": "123 MAIN ST, RENO, NV 89501",
            "label": "ADDRESS",
            "properties": {"address": "123 MAIN ST", "city": "RENO", "state": "NV", "zip": "89501"}
        },
        {
            "id": "PPP_LOAN_998877",
            "label": "PPP_LOAN",
            "properties": {"loan_number": "998877", "amount": "150000.00"}
        }
    ]
    file_path.write_text(json.dumps(data), encoding="utf-8")
    return file_path


@pytest.fixture
def dict_root_nodes_json(tmp_path):
    """Fix 6 Verification: Support dictionary root JSON files."""
    file_path = tmp_path / "dict_nodes.json"
    data = {
        "nodes": [
            {
                "id": "NODE_001",
                "label": "ORGANIZATION",
                "properties": {"name": "GLOBAL TECH INC"}
            }
        ]
    }
    file_path.write_text(json.dumps(data), encoding="utf-8")
    return file_path


@pytest.fixture
def sample_edges_json(tmp_path):
    file_path = tmp_path / "edges.json"
    data = [
        {
            "source_id": "ACME CORP LLC",
            "source_label": "ORGANIZATION",
            "type": "OWNS",
            "target_id": "APN-123-456",
            "target_label": "PROPERTY",
            "properties": {"confidence": 0.95}
        },
        {
            "source_id": "ACME CORP LLC",
            "source_label": "ORGANIZATION",
            "type": "REGISTERED_AT",
            "target_id": "123 MAIN ST, RENO, NV 89501",
            "target_label": "ADDRESS",
            "properties": {}
        }
    ]
    file_path.write_text(json.dumps(data), encoding="utf-8")
    return file_path


@pytest.fixture
def sample_ppp_csv(tmp_path):
    file_path = tmp_path / "ppp_loans.csv"
    content = (
        "BorrowerName,BorrowerAddress,City,State,Zip,LoanNumber,CurrentApprovalAmount,ForgivenessAmount\n"
        "STEWART INDUSTRIES LLC,1077 PACIFIC COAST HWY #247,SEAL BEACH,CA,90740,PPP-001,1128327.50,1137910.56\n"
        "APEX HOLDINGS INC,3311 BOUNTY CIR,HUNTINGTON BEACH,CA,92648,PPP-002,$50,000.00,$50,000.00\n"
    )
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def latin1_ppp_csv(tmp_path):
    """Fix 6 Verification: Non-UTF8 CSV files (Latin-1) parse cleanly without UnicodeDecodeError."""
    file_path = tmp_path / "latin1_ppp.csv"
    content = (
        "BorrowerName,BorrowerAddress,City,State,Zip,LoanNumber,CurrentApprovalAmount\n"
        "CAFÉ ENTERPRISES LLC,100 MAIN ST,RENO,NV,89501,PPP-LATIN1,50000\n"
    )
    file_path.write_bytes(content.encode("iso-8859-1"))
    return file_path


@pytest.fixture
def sample_sos_csv(tmp_path):
    file_path = tmp_path / "sos_records.csv"
    content = (
        "entity_name,sos_file_num,registered_agent,agent_address,status\n"
        "DESERT SUN ENTERPRISES LLC,E0123452020-1,JOHN SMITH,100 S VIRGINIA ST SUITE 10 RENO NV 89501,Active\n"
        "SIERRA TECH CORP,C0987652019-2,JANE DOE,456 COMMERCIAL ROW RENO NV 89501,Active\n"
        "LLC,,THE,100 S VIRGINIA ST RENO NV 89501,Active\n"
    )
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_property_csv(tmp_path):
    file_path = tmp_path / "property_records.csv"
    content = (
        "apn,owner_name,situs_address,mail_address,assessed_value\n"
        "178-431-14,STEWART INDUSTRIES LLC,3311 BOUNTY CIR,1077 PACIFIC COAST HWY #247,$750,000\n"
        "151-234-09,ROBERT JOHNSON,21951 BROOKHURST ST,PO BOX 100 RENO NV 89501,320000\n"
    )
    file_path.write_text(content, encoding="utf-8")
    return file_path


class TestNumericCleaner:
    def test_clean_numeric_formats(self):
        assert _clean_numeric("$1,128,327.50") == 1128327.50
        assert _clean_numeric("50000") == 50000.0
        assert _clean_numeric(None) == 0.0
        assert _clean_numeric("invalid", default=1.0) == 1.0


class TestJsonParsers:
    def test_parse_nodes_json(self, sample_nodes_json):
        nodes = parse_nodes_json(sample_nodes_json)
        assert len(nodes) == 4
        node_types = {n.node_type for n in nodes}
        assert "ORGANIZATION" in node_types
        assert "PROPERTY" in node_types
        assert "ADDRESS" in node_types
        assert "PPP_LOAN" in node_types

    def test_parse_dict_root_nodes_json(self, dict_root_nodes_json):
        nodes = parse_nodes_json(dict_root_nodes_json)
        assert len(nodes) == 1
        assert nodes[0].node_id == "NODE_001"

    def test_parse_edges_json(self, sample_edges_json):
        edges = parse_edges_json(sample_edges_json)
        assert len(edges) == 2
        edge_types = {e.edge_type for e in edges}
        assert "OWNS" in edge_types
        assert "REGISTERED_AT" in edge_types
        assert edges[0].confidence == 0.95


class TestCsvParsers:
    def test_parse_ppp_loans_csv(self, sample_ppp_csv):
        result = parse_ppp_loans_csv(sample_ppp_csv)
        assert result.node_count >= 6  # 2 ORGs, 2 PPP_LOANs, 2 ADDRESSes
        assert result.edge_count >= 4  # 2 RECEIVED_PPP, 2 LOCATED_IN

        org_nodes = [n for n in result.nodes if n.node_type == "ORGANIZATION"]
        assert len(org_nodes) == 2
        
        ppp_edges = [e for e in result.edges if e.edge_type == "RECEIVED_PPP"]
        assert len(ppp_edges) == 2

    def test_latin1_csv_encoding(self, latin1_ppp_csv):
        result = parse_ppp_loans_csv(latin1_ppp_csv)
        assert result.node_count >= 2
        org_node = [n for n in result.nodes if n.node_type == "ORGANIZATION"][0]
        assert "CAF" in org_node.label.upper()

    def test_parse_sos_records_csv(self, sample_sos_csv):
        result = parse_sos_records_csv(sample_sos_csv)
        assert result.node_count >= 6  # 3 ORGs, 3 PERSONs (agents), 3 ADDRESSes
        
        reg_edges = [e for e in result.edges if e.edge_type == "REGISTERED_AT"]
        officer_edges = [e for e in result.edges if e.edge_type == "OFFICER_OF"]
        assert len(reg_edges) == 3
        assert len(officer_edges) == 3

    def test_parse_sos_records_node_id_uniqueness(self, sample_sos_csv):
        """Fix 5 Verification: Empty sos_file_num and stop-word names do not create ORG_ or PERSON_ collisions."""
        result = parse_sos_records_csv(sample_sos_csv)
        node_ids = [n.node_id for n in result.nodes]
        
        assert "ORG_" not in node_ids
        assert "PERSON_" not in node_ids
        assert len(node_ids) == len(set(node_ids))  # All node IDs are strictly unique!

    def test_parse_property_records_csv(self, sample_property_csv):
        result = parse_property_records_csv(sample_property_csv)
        
        prop_nodes = [n for n in result.nodes if n.node_type == "PROPERTY"]
        assert len(prop_nodes) == 2
        
        owns_edges = [e for e in result.edges if e.edge_type == "OWNS"]
        assert len(owns_edges) == 2

    def test_ingestion_result_merge(self, sample_ppp_csv, sample_sos_csv):
        res1 = parse_ppp_loans_csv(sample_ppp_csv)
        res2 = parse_sos_records_csv(sample_sos_csv)
        merged = res1.merge(res2)
        assert merged.node_count <= res1.node_count + res2.node_count
        assert merged.edge_count <= res1.edge_count + res2.edge_count
