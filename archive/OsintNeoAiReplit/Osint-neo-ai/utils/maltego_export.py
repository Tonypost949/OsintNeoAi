"""
Maltego Graph Exchange (.mtgx) exporter.

Produces a ZIP archive containing Graphs/Graph1.graphml that Maltego
can open directly via File → Import → Import Graph.

Entity type mapping:
  Person       → maltego.Person
  Email        → maltego.EmailAddress
  Organization → maltego.Organization
  Location     → maltego.Location
  IP           → maltego.IPv4Address
  Domain       → maltego.Domain
  Phone        → maltego.PhoneNumber
  Document     → maltego.Document
  Legal        → maltego.Phrase
  (default)    → maltego.Phrase
"""

import io
import math
import zipfile
import xml.etree.ElementTree as ET
from xml.dom import minidom


# ── Entity-type mapping ───────────────────────────────────────────────────────

_TYPE_MAP = {
    "Person":       ("maltego.Person",        "person.fullname",              "Full Name"),
    "Email":        ("maltego.EmailAddress",   "email.address",                "Email Address"),
    "Organization": ("maltego.Organization",   "organization.name",            "Name"),
    "Location":     ("maltego.Location",       "location.name",                "Name"),
    "IP":           ("maltego.IPv4Address",    "ipv4-address.ipv4address",     "IP Address"),
    "Domain":       ("maltego.Domain",         "domain.name",                  "Domain Name"),
    "Phone":        ("maltego.PhoneNumber",    "phonenumber.phonenumber",      "Phone Number"),
    "Document":     ("maltego.Document",       "document.title",               "Title"),
    "Legal":        ("maltego.Phrase",         "phrase.phrase",                "Phrase"),
    "Vehicle":      ("maltego.Phrase",         "phrase.phrase",                "Phrase"),
    "Device":       ("maltego.Phrase",         "phrase.phrase",                "Phrase"),
}

_DEFAULT_TYPE = ("maltego.Phrase", "phrase.phrase", "Phrase")

_RISK_COLORS = {
    "High":    "#FF4B4B",
    "Medium":  "#FFAA00",
    "Low":     "#00CC66",
    "Unknown": "#FFFCF3",
}


def _maltego_entity_xml(maltego_type: str, value: str,
                        prop_name: str, prop_display: str,
                        notes: str = "", source: str = "",
                        risk: str = "Unknown") -> str:
    """Return the inner CDATA XML string for a Maltego entity node."""
    value = (value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    notes = (notes or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    source = (source or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    lines = [
        f'<MaltegoEntity type="{maltego_type}">',
        f'  <Value>{value}</Value>',
        f'  <Weight>100</Weight>',
        f'  <UiVisible>true</UiVisible>',
        f'  <Properties>',
        f'    <Property name="{prop_name}" type="string" displayName="{prop_display}">',
        f'      <Value>{value}</Value>',
        f'    </Property>',
        f'    <Property name="osint.risk" type="string" displayName="Risk Level">',
        f'      <Value>{risk}</Value>',
        f'    </Property>',
        f'    <Property name="osint.notes" type="string" displayName="Notes">',
        f'      <Value>{notes}</Value>',
        f'    </Property>',
        f'    <Property name="osint.source" type="string" displayName="Source">',
        f'      <Value>{source}</Value>',
        f'    </Property>',
        f'  </Properties>',
        f'</MaltegoEntity>',
    ]
    return "\n".join(lines)


def _layout_circle(n: int, radius: float = 600.0):
    """Return (x, y) positions arranged in a circle."""
    positions = []
    for i in range(n):
        angle = 2 * math.pi * i / max(n, 1)
        x = radius + radius * math.cos(angle)
        y = radius + radius * math.sin(angle)
        positions.append((round(x, 1), round(y, 1)))
    return positions


def build_mtgx(entities: list[dict], relationships: list[dict]) -> bytes:
    """
    Build a .mtgx file in memory and return its bytes.

    entities      – list of dicts from get_all_entities()
    relationships – list of dicts from get_all_relationships()

    Returns raw bytes suitable for st.download_button.
    """

    # ── GraphML skeleton ──────────────────────────────────────────────────────
    NS = "http://graphml.graphdrawing.org/graphml"
    ET.register_namespace("", NS)
    root = ET.Element(f"{{{NS}}}graphml")

    def key(kid, for_, name, atype):
        k = ET.SubElement(root, f"{{{NS}}}key")
        k.set("id", kid)
        k.set("for", for_)
        k.set("attr.name", name)
        k.set("attr.type", atype)

    key("d0", "node", "pos_x",             "double")
    key("d1", "node", "pos_y",             "double")
    key("d2", "node", "boost",             "int")
    key("d3", "node", "retained",          "boolean")
    key("d4", "node", "iconurl",           "string")
    key("d5", "node", "color",             "string")
    key("d6", "node", "maltego.genentity", "string")
    key("d7", "edge", "label",             "string")
    key("d8", "edge", "weight",            "double")

    graph_el = ET.SubElement(root, f"{{{NS}}}graph")
    graph_el.set("id", "G")
    graph_el.set("edgedefault", "directed")

    # ── Build entity_id → node_id map ─────────────────────────────────────────
    positions = _layout_circle(len(entities))
    eid_to_nid: dict[str, str] = {}   # entity_id  → "n0", "n1", …
    label_to_nid: dict[str, str] = {} # label text → "n0", "n1", …  (for loose refs)

    for idx, ent in enumerate(entities):
        eid      = ent.get("entity_id", f"ENT-{idx}")
        label    = ent.get("label", eid)
        etype    = ent.get("type", "Other")
        risk     = ent.get("risk_level", "Unknown")
        notes    = ent.get("notes", "")
        source   = ent.get("source", "")
        nid      = f"n{idx}"

        eid_to_nid[eid]   = nid
        label_to_nid[label] = nid

        maltego_type, prop_name, prop_display = _TYPE_MAP.get(etype, _DEFAULT_TYPE)
        color = _RISK_COLORS.get(risk, "#FFFCF3")
        x, y  = positions[idx]

        node_el = ET.SubElement(graph_el, f"{{{NS}}}node")
        node_el.set("id", nid)

        def nd(kid, val):
            d = ET.SubElement(node_el, f"{{{NS}}}data")
            d.set("key", kid)
            d.text = str(val)

        nd("d0", x)
        nd("d1", y)
        nd("d2", 0)
        nd("d3", "false")
        nd("d4", "")
        nd("d5", color)

        inner = _maltego_entity_xml(maltego_type, label,
                                    prop_name, prop_display,
                                    notes, source, risk)
        d6 = ET.SubElement(node_el, f"{{{NS}}}data")
        d6.set("key", "d6")
        # Use CDATA-like approach: store raw XML as text
        d6.text = inner

    # ── Relationships → edges ─────────────────────────────────────────────────
    edge_idx = 0
    for rel in relationships:
        src_raw  = rel.get("source_entity", "")
        tgt_raw  = rel.get("target_entity", "")
        rel_type = rel.get("relationship_type", "Related")
        conf     = rel.get("confidence", "Medium")

        # Resolve source
        src_nid = eid_to_nid.get(src_raw) or label_to_nid.get(src_raw)
        tgt_nid = eid_to_nid.get(tgt_raw) or label_to_nid.get(tgt_raw)

        if src_nid is None or tgt_nid is None:
            continue   # skip unresolvable references

        edge_el = ET.SubElement(graph_el, f"{{{NS}}}edge")
        edge_el.set("id", f"e{edge_idx}")
        edge_el.set("source", src_nid)
        edge_el.set("target", tgt_nid)
        edge_idx += 1

        d7 = ET.SubElement(edge_el, f"{{{NS}}}data")
        d7.set("key", "d7")
        d7.text = rel_type

        weight_map = {"High": "1.0", "Medium": "0.6", "Low": "0.3"}
        d8 = ET.SubElement(edge_el, f"{{{NS}}}data")
        d8.set("key", "d8")
        d8.text = weight_map.get(conf, "0.5")

    # ── Serialise GraphML to pretty XML ──────────────────────────────────────
    raw_xml = ET.tostring(root, encoding="unicode")
    pretty  = minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8")

    # ── Pack into .mtgx ZIP ───────────────────────────────────────────────────
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Graphs/Graph1.graphml", pretty)
    return buf.getvalue()
