"""
Data Ingestion and Streamed Parser Engine for OSINT Datasets.
Handles baseline JSON graph files, SBA PPP Loans, NV/CA SOS Corporate Records,
and Parcel/Property Records CSVs.
"""
import json
import csv
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union, Iterator, Set
from pydantic import BaseModel, Field

from src.core.schemas import NodeDTO, EdgeDTO
from src.core.normalizers import normalize_address, normalize_entity_name


class IngestionResult(BaseModel):
    """Container DTO for aggregated node and edge ingestion results."""
    nodes: List[NodeDTO] = Field(default_factory=list, description="List of unique ingested nodes")
    edges: List[EdgeDTO] = Field(default_factory=list, description="List of ingested relationship edges")

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def merge(self, other: "IngestionResult") -> "IngestionResult":
        """Merges another IngestionResult into self, deduplicating nodes by node_id."""
        existing_node_ids = {n.node_id for n in self.nodes}
        new_nodes = list(self.nodes)
        for n in other.nodes:
            if n.node_id not in existing_node_ids:
                new_nodes.append(n)
                existing_node_ids.add(n.node_id)

        existing_edge_ids = {e.edge_id for e in self.edges}
        new_edges = list(self.edges)
        for e in other.edges:
            if e.edge_id not in existing_edge_ids:
                new_edges.append(e)
                existing_edge_ids.add(e.edge_id)

        return IngestionResult(nodes=new_nodes, edges=new_edges)


def _clean_numeric(val: Any, default: float = 0.0) -> float:
    """Safely converts string/number with currency symbols and commas to float."""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    cleaned = re.sub(r"[^\d\.-]", "", str(val))
    try:
        return float(cleaned) if cleaned else default
    except ValueError:
        return default


def _read_csv_rows(file_path: Path) -> List[Dict[str, str]]:
    """
    Reads a CSV file with fallback encoding support (utf-8-sig, utf-8, latin-1, cp1252).
    Handles unescaped comma extra columns cleanly to prevent AttributeError.
    """
    encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
    raw_rows = None
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc, errors="strict") as f:
                reader = csv.DictReader(f)
                raw_rows = list(reader)
                break
        except (UnicodeDecodeError, UnicodeError):
            continue
    if raw_rows is None:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            raw_rows = list(reader)

    cleaned_rows: List[Dict[str, str]] = []
    for row in raw_rows:
        if not isinstance(row, dict):
            continue
        clean_row: Dict[str, str] = {}
        for k, v in row.items():
            if k is not None and v is not None:
                clean_row[str(k).strip()] = str(v).strip()
        cleaned_rows.append(clean_row)
    return cleaned_rows


def parse_nodes_json(path: Union[str, Path]) -> List[NodeDTO]:
    """
    Stream and load baseline nodes.json file (17.4k nodes).
    Supports array root JSON and dictionary root JSON (`{"nodes": [...]}`).
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"nodes.json file not found at: {file_path}")

    nodes: List[NodeDTO] = []
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = data.get("nodes") or data.get("data") or data.get("items") or (list(data.values())[0] if data else [])
    if not isinstance(data, list):
        data = []

    for item in data:
        if not isinstance(item, dict):
            continue
        node_id = str(item.get("id") or item.get("node_id") or "").strip()
        if not node_id:
            continue

        raw_label = str(item.get("label") or item.get("node_type") or "ORGANIZATION").upper().strip()
        props = item.get("properties") or item.get("metadata") or {}
        if not isinstance(props, dict):
            props = {}

        # Extract primary human-readable display label
        display_label = (
            item.get("label")
            if "id" in item and "label" in item and item.get("label") != raw_label
            else (
                props.get("name")
                or props.get("address")
                or props.get("apn")
                or props.get("borrower_name")
                or item.get("label")
                or node_id
            )
        )
        display_label = str(display_label or "").strip()

        # Handle address node normalization
        address_id = props.get("address_id") or item.get("address_id")
        if raw_label == "ADDRESS":
            city_val = props.get("city") if props.get("city") is not None else ""
            state_val = props.get("state") if props.get("state") is not None else ""
            zip_val = (props.get("zip") or props.get("zip_code")) if (props.get("zip") or props.get("zip_code")) is not None else ""
            norm_addr = normalize_address(display_label, city_val, state_val, zip_val)
            address_id = norm_addr.address_hash

        nodes.append(
            NodeDTO(
                node_id=node_id,
                node_type=raw_label,
                label=display_label,
                normalized_label=display_label.upper(),
                address_id=address_id,
                metadata=props
            )
        )

    return nodes


def parse_edges_json(path: Union[str, Path]) -> List[EdgeDTO]:
    """
    Stream and load baseline edges.json file (18.7k edges).
    Supports array root JSON and dictionary root JSON (`{"edges": [...]}`).
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"edges.json file not found at: {file_path}")

    edges: List[EdgeDTO] = []
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = data.get("edges") or data.get("data") or data.get("items") or (list(data.values())[0] if data else [])
    if not isinstance(data, list):
        data = []

    for item in data:
        if not isinstance(item, dict):
            continue
        source_id = str(item.get("source_id", "")).strip()
        target_id = str(item.get("target_id", "")).strip()
        if not source_id or not target_id:
            continue

        edge_type = str(item.get("type") or item.get("edge_type") or "ASSOCIATED_WITH").upper().strip()
        props = item.get("properties") or item.get("metadata") or {}
        if not isinstance(props, dict):
            props = {}

        edge_id = item.get("edge_id") or f"{source_id}_{edge_type}_{target_id}"
        confidence = _clean_numeric(item.get("confidence") if "confidence" in item else props.get("confidence"), default=1.0)
        confidence = min(max(confidence, 0.0), 1.0)

        meta = {
            "source_label": item.get("source_label"),
            "target_label": item.get("target_label"),
            **props
        }

        edges.append(
            EdgeDTO(
                edge_id=edge_id,
                source_id=source_id,
                target_id=target_id,
                edge_type=edge_type,
                confidence=confidence,
                metadata=meta
            )
        )

    return edges


def parse_ppp_loans_csv(path: Union[str, Path]) -> IngestionResult:
    """
    Parse SBA PPP Loan CSV records into graph nodes and edges.
    Generates ORGANIZATION, PPP_LOAN, and ADDRESS nodes and RECEIVED_PPP, LOCATED_IN edges.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"PPP loans CSV file not found at: {file_path}")

    nodes_map: Dict[str, NodeDTO] = {}
    edges_map: Dict[str, EdgeDTO] = {}

    rows = _read_csv_rows(file_path)
    for row in rows:
        row_lower = {k.strip().lower(): v.strip() for k, v in row.items() if k and v}
        
        borrower_name = row_lower.get("borrowername") or row_lower.get("borrower_name") or row_lower.get("borrower") or ""
        if not borrower_name:
            continue

        borrower_addr = row_lower.get("borroweraddress") or row_lower.get("borrower_address") or row_lower.get("address") or ""
        city = row_lower.get("city") or row_lower.get("borrowercity") or ""
        state = row_lower.get("state") or row_lower.get("borrowerstate") or ""
        zip_code = row_lower.get("zip") or row_lower.get("borrowerzip") or ""

        loan_num = row_lower.get("loannumber") or row_lower.get("loan_number") or row_lower.get("id") or ""
        approval_amt = _clean_numeric(row_lower.get("currentapprovalamount") or row_lower.get("approval_amount") or row_lower.get("amount"))
        forgiven_amt = _clean_numeric(row_lower.get("forgivenessamount") or row_lower.get("forgiven_amount"))

        # 1. ORGANIZATION Node
        norm_name = normalize_entity_name(borrower_name, is_business=True)
        if norm_name.core_key:
            clean_key = norm_name.core_key.replace(" ", "_")
            org_id = f"ORG_{clean_key}"
        else:
            raw_hash = hashlib.sha256(borrower_name.strip().encode("utf-8")).hexdigest()[:12]
            org_id = f"ORG_HASH_{raw_hash}"
        
        if org_id not in nodes_map:
            nodes_map[org_id] = NodeDTO(
                node_id=org_id,
                node_type="ORGANIZATION",
                label=norm_name.clean_name,
                normalized_label=norm_name.core_key,
                metadata={
                    "raw_name": borrower_name,
                    "soundex": norm_name.soundex,
                    "double_metaphone": list(norm_name.double_metaphone)
                }
            )

        # 2. PPP_LOAN Node
        if loan_num:
            effective_loan_id = loan_num
        else:
            synthetic_seed = f"{borrower_name}_{approval_amt}"
            effective_loan_id = f"SYN_{hashlib.sha256(synthetic_seed.encode('utf-8')).hexdigest()[:12]}"
        
        loan_node_id = f"PPP_LOAN_{effective_loan_id}"
        
        if loan_node_id not in nodes_map:
            nodes_map[loan_node_id] = NodeDTO(
                node_id=loan_node_id,
                node_type="PPP_LOAN",
                label=f"PPP Loan {effective_loan_id}",
                normalized_label=f"PPP LOAN {effective_loan_id}",
                metadata={
                    "loan_number": effective_loan_id,
                    "borrower_name": borrower_name,
                    "amount": approval_amt,
                    "forgiven_amount": forgiven_amt,
                    "status": row_lower.get("loanstatus", "APPROVED")
                }
            )

        # RECEIVED_PPP Edge
        edge_ppp_id = f"{org_id}_RECEIVED_PPP_{loan_node_id}"
        if edge_ppp_id not in edges_map:
            edges_map[edge_ppp_id] = EdgeDTO(
                edge_id=edge_ppp_id,
                source_id=org_id,
                target_id=loan_node_id,
                edge_type="RECEIVED_PPP",
                confidence=1.0,
                metadata={"amount": approval_amt}
            )

        # 3. ADDRESS Node & LOCATED_IN Edge
        if borrower_addr:
            norm_addr = normalize_address(borrower_addr, city, state, zip_code)
            addr_node_id = f"ADDR_{norm_addr.address_hash[:16]}"
            
            if addr_node_id not in nodes_map:
                nodes_map[addr_node_id] = NodeDTO(
                    node_id=addr_node_id,
                    node_type="ADDRESS",
                    label=norm_addr.normalized_str,
                    normalized_label=norm_addr.normalized_str,
                    address_id=norm_addr.address_hash,
                    metadata={
                        "street": norm_addr.street,
                        "city": norm_addr.city,
                        "state": norm_addr.state,
                        "zip_code": norm_addr.zip_code,
                        "unit": norm_addr.unit,
                        "address_hash": norm_addr.address_hash
                    }
                )

            nodes_map[org_id].address_id = norm_addr.address_hash

            edge_loc_id = f"{org_id}_LOCATED_IN_{addr_node_id}"
            if edge_loc_id not in edges_map:
                edges_map[edge_loc_id] = EdgeDTO(
                    edge_id=edge_loc_id,
                    source_id=org_id,
                    target_id=addr_node_id,
                    edge_type="LOCATED_IN",
                    confidence=1.0,
                    metadata={"address_type": "BORROWER_LOCATION"}
                )

    return IngestionResult(nodes=list(nodes_map.values()), edges=list(edges_map.values()))


def parse_sos_records_csv(path: Union[str, Path]) -> IngestionResult:
    """
    Parse Secretary of State (SOS) Corporate Entity CSV records.
    Generates ORGANIZATION, PERSON, ADDRESS nodes and REGISTERED_AT, OFFICER_OF edges.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"SOS CSV file not found at: {file_path}")

    nodes_map: Dict[str, NodeDTO] = {}
    edges_map: Dict[str, EdgeDTO] = {}

    rows = _read_csv_rows(file_path)
    for row in rows:
        row_lower = {k.strip().lower(): v.strip() for k, v in row.items() if k and v}

        entity_name = (
            row_lower.get("entity_name")
            or row_lower.get("entityname")
            or row_lower.get("business_name")
            or row_lower.get("corporation_name")
            or ""
        )
        if not entity_name:
            continue

        sos_num = row_lower.get("sos_file_num") or row_lower.get("sos_file_number") or row_lower.get("file_num") or row_lower.get("entity_id") or ""
        reg_agent = row_lower.get("registered_agent") or row_lower.get("registered_agent_name") or row_lower.get("agent_name") or row_lower.get("agent") or ""
        agent_addr = row_lower.get("agent_address") or row_lower.get("registered_agent_address") or row_lower.get("registered_address") or row_lower.get("address") or ""
        status = row_lower.get("status") or row_lower.get("entity_status") or "ACTIVE"

        # 1. ORGANIZATION Node
        norm_entity = normalize_entity_name(entity_name, is_business=True)
        if sos_num:
            org_id = f"ORG_SOS_{sos_num}"
        elif norm_entity.core_key:
            clean_key = norm_entity.core_key.replace(" ", "_")
            org_id = f"ORG_{clean_key}"
        else:
            raw_hash = hashlib.sha256(entity_name.strip().encode("utf-8")).hexdigest()[:12]
            org_id = f"ORG_HASH_{raw_hash}"

        if org_id not in nodes_map:
            nodes_map[org_id] = NodeDTO(
                node_id=org_id,
                node_type="ORGANIZATION",
                label=norm_entity.clean_name,
                normalized_label=norm_entity.core_key,
                metadata={
                    "raw_name": entity_name,
                    "sos_file_num": sos_num,
                    "status": status,
                    "soundex": norm_entity.soundex
                }
            )

        # 2. ADDRESS Node & REGISTERED_AT Edge
        if agent_addr:
            norm_addr = normalize_address(agent_addr)
            addr_node_id = f"ADDR_{norm_addr.address_hash[:16]}"

            if addr_node_id not in nodes_map:
                nodes_map[addr_node_id] = NodeDTO(
                    node_id=addr_node_id,
                    node_type="ADDRESS",
                    label=norm_addr.normalized_str,
                    normalized_label=norm_addr.normalized_str,
                    address_id=norm_addr.address_hash,
                    metadata={
                        "street": norm_addr.street,
                        "city": norm_addr.city,
                        "state": norm_addr.state,
                        "zip_code": norm_addr.zip_code,
                        "address_hash": norm_addr.address_hash
                    }
                )

            nodes_map[org_id].address_id = norm_addr.address_hash

            edge_reg_id = f"{org_id}_REGISTERED_AT_{addr_node_id}"
            if edge_reg_id not in edges_map:
                edges_map[edge_reg_id] = EdgeDTO(
                    edge_id=edge_reg_id,
                    source_id=org_id,
                    target_id=addr_node_id,
                    edge_type="REGISTERED_AT",
                    confidence=1.0,
                    metadata={"address_type": "REGISTERED_AGENT_ADDRESS"}
                )

        # 3. PERSON Node (Registered Agent / Officer) & OFFICER_OF Edge
        officer_name = row_lower.get("officer_name") or reg_agent
        if officer_name:
            norm_agent = normalize_entity_name(officer_name, is_business=False)
            if norm_agent.core_key:
                clean_key = norm_agent.core_key.replace(" ", "_")
                person_node_id = f"PERSON_{clean_key}"
            else:
                raw_hash = hashlib.sha256(officer_name.strip().encode("utf-8")).hexdigest()[:12]
                person_node_id = f"PERSON_HASH_{raw_hash}"

            if person_node_id not in nodes_map:
                nodes_map[person_node_id] = NodeDTO(
                    node_id=person_node_id,
                    node_type="PERSON",
                    label=norm_agent.clean_name,
                    normalized_label=norm_agent.core_key,
                    metadata={
                        "raw_name": officer_name,
                        "soundex": norm_agent.soundex
                    }
                )

            edge_off_id = f"{person_node_id}_OFFICER_OF_{org_id}"
            if edge_off_id not in edges_map:
                edges_map[edge_off_id] = EdgeDTO(
                    edge_id=edge_off_id,
                    source_id=person_node_id,
                    target_id=org_id,
                    edge_type="OFFICER_OF",
                    confidence=1.0,
                    metadata={"role": row_lower.get("officer_title", "Registered Agent / Officer")}
                )

    return IngestionResult(nodes=list(nodes_map.values()), edges=list(edges_map.values()))


def parse_property_records_csv(path: Union[str, Path]) -> IngestionResult:
    """
    Parse Parcel / Property Ownership CSV records.
    Generates PROPERTY, ORGANIZATION/PERSON, ADDRESS nodes and OWNS, LOCATED_IN edges.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Property CSV file not found at: {file_path}")

    nodes_map: Dict[str, NodeDTO] = {}
    edges_map: Dict[str, EdgeDTO] = {}

    biz_keywords = {"LLC", "INC", "CORP", "CORPORATION", "CO", "HOLDINGS", "PROPERTIES", "TRUST", "LTD", "LP", "PARTNERSHIP"}

    rows = _read_csv_rows(file_path)
    for row in rows:
        row_lower = {k.strip().lower(): v.strip() for k, v in row.items() if k and v}

        apn = row_lower.get("apn") or row_lower.get("parcel_id") or row_lower.get("parcel_num") or ""
        if not apn:
            continue

        owner_raw = row_lower.get("owner_name") or row_lower.get("owner") or row_lower.get("grantee") or ""
        situs_addr = row_lower.get("situs_address") or row_lower.get("situs") or row_lower.get("property_address") or ""
        mail_addr = row_lower.get("mail_address") or row_lower.get("mailing_address") or ""
        assessed_val = _clean_numeric(row_lower.get("assessed_value") or row_lower.get("assessed_val") or row_lower.get("total_value"))

        # 1. PROPERTY Node
        prop_node_id = f"PROP_{apn}"
        if prop_node_id not in nodes_map:
            nodes_map[prop_node_id] = NodeDTO(
                node_id=prop_node_id,
                node_type="PROPERTY",
                label=f"Parcel {apn}",
                normalized_label=f"PARCEL {apn.upper()}",
                metadata={
                    "apn": apn,
                    "assessed_value": assessed_val
                }
            )

        # 2. Owner Node (ORGANIZATION or PERSON) & OWNS Edge
        if owner_raw:
            tokens = set(re.findall(r"\b[A-Z0-9]+\b", owner_raw.upper()))
            is_biz = bool(tokens.intersection(biz_keywords))

            norm_owner = normalize_entity_name(owner_raw, is_business=is_biz)
            node_type = "ORGANIZATION" if is_biz else "PERSON"
            prefix = "ORG" if is_biz else "PERSON"
            
            if norm_owner.core_key:
                clean_key = norm_owner.core_key.replace(" ", "_")
                owner_node_id = f"{prefix}_{clean_key}"
            else:
                raw_hash = hashlib.sha256(owner_raw.strip().encode("utf-8")).hexdigest()[:12]
                owner_node_id = f"{prefix}_HASH_{raw_hash}"

            if owner_node_id not in nodes_map:
                nodes_map[owner_node_id] = NodeDTO(
                    node_id=owner_node_id,
                    node_type=node_type,
                    label=norm_owner.clean_name,
                    normalized_label=norm_owner.core_key,
                    metadata={
                        "raw_name": owner_raw,
                        "soundex": norm_owner.soundex
                    }
                )

            edge_owns_id = f"{owner_node_id}_OWNS_{prop_node_id}"
            if edge_owns_id not in edges_map:
                edges_map[edge_owns_id] = EdgeDTO(
                    edge_id=edge_owns_id,
                    source_id=owner_node_id,
                    target_id=prop_node_id,
                    edge_type="OWNS",
                    confidence=1.0,
                    metadata={"assessed_value": assessed_val}
                )

        # 3. Physical Property Address (Situs) & LOCATED_IN Edge
        if situs_addr:
            norm_situs = normalize_address(situs_addr)
            situs_node_id = f"ADDR_{norm_situs.address_hash[:16]}"

            if situs_node_id not in nodes_map:
                nodes_map[situs_node_id] = NodeDTO(
                    node_id=situs_node_id,
                    node_type="ADDRESS",
                    label=norm_situs.normalized_str,
                    normalized_label=norm_situs.normalized_str,
                    address_id=norm_situs.address_hash,
                    metadata={
                        "street": norm_situs.street,
                        "city": norm_situs.city,
                        "state": norm_situs.state,
                        "zip_code": norm_situs.zip_code,
                        "address_type": "SITUS"
                    }
                )

            nodes_map[prop_node_id].address_id = norm_situs.address_hash

            edge_loc_id = f"{prop_node_id}_LOCATED_IN_{situs_node_id}"
            if edge_loc_id not in edges_map:
                edges_map[edge_loc_id] = EdgeDTO(
                    edge_id=edge_loc_id,
                    source_id=prop_node_id,
                    target_id=situs_node_id,
                    edge_type="LOCATED_IN",
                    confidence=1.0,
                    metadata={"address_type": "PROPERTY_SITUS"}
                )

        # 4. Owner Mailing Address & LOCATED_IN Edge
        if mail_addr:
            norm_mail = normalize_address(mail_addr)
            mail_node_id = f"ADDR_{norm_mail.address_hash[:16]}"

            if mail_node_id not in nodes_map:
                nodes_map[mail_node_id] = NodeDTO(
                    node_id=mail_node_id,
                    node_type="ADDRESS",
                    label=norm_mail.normalized_str,
                    normalized_label=norm_mail.normalized_str,
                    address_id=norm_mail.address_hash,
                    metadata={
                        "street": norm_mail.street,
                        "city": norm_mail.city,
                        "state": norm_mail.state,
                        "zip_code": norm_mail.zip_code,
                        "address_type": "MAILING"
                    }
                )

            if owner_raw:
                edge_mail_id = f"{owner_node_id}_LOCATED_IN_{mail_node_id}"
                if edge_mail_id not in edges_map:
                    edges_map[edge_mail_id] = EdgeDTO(
                        edge_id=edge_mail_id,
                        source_id=owner_node_id,
                        target_id=mail_node_id,
                        edge_type="LOCATED_IN",
                        confidence=1.0,
                        metadata={"address_type": "OWNER_MAILING"}
                    )

    return IngestionResult(nodes=list(nodes_map.values()), edges=list(edges_map.values()))
