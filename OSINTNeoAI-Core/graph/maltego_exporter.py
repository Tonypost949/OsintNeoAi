import xml.etree.ElementTree as ET

class MaltegoExporter:
    """Consolidated exporter translating structured graph entities into Maltego XML Link-Analysis packages."""
    
    def __init__(self):
        self.entities = []
        self.links = []

    def add_entity(self, entity_id, label, entity_type, properties=None):
        """Register a node entity to be compiled into the Maltego graph space."""
        props = properties or {}
        self.entities.append({
            "id": entity_id,
            "label": label,
            "type": entity_type,
            "properties": props
        })

    def add_link(self, source_id, target_id, relation_type):
        """Register a directed link connection between two registered entities."""
        self.links.append({
            "source": source_id,
            "target": target_id,
            "relation": relation_type
        })

    def export_to_xml(self, output_path):
        """Generate a valid Maltego MTGL/XML document structure."""
        root = ET.Element("MaltegoMessage")
        graph = ET.SubElement(root, "Graph")
        
        entities_node = ET.SubElement(graph, "Entities")
        for ent in self.entities:
            ent_el = ET.SubElement(entities_node, "Entity", Type=f"maltego.{ent['type'].lower()}")
            
            val_node = ET.SubElement(ent_el, "Value")
            val_node.text = ent['label']
            
            props_node = ET.SubElement(ent_el, "AdditionalFields")
            for k, v in ent['properties'].items():
                field_el = ET.SubElement(props_node, "Field", Name=k, DisplayName=k.replace("_", " ").title())
                field_el.text = str(v)
                
        links_node = ET.SubElement(graph, "Links")
        for lk in self.links:
            # We map relationships using standard directed connectors
            link_el = ET.SubElement(links_node, "Link", Type="maltego.link.directed")
            ET.SubElement(link_el, "Source").text = lk['source']
            ET.SubElement(link_el, "Target").text = lk['target']
            ET.SubElement(link_el, "Relation").text = lk['relation']

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        
        try:
            with open(output_path, "wb") as f:
                tree.write(f, encoding="utf-8", xml_declaration=True)
            print(f"[Maltego] Successfully exported {len(self.entities)} entities and {len(self.links)} links to {output_path}")
        except Exception as e:
            print(f"[Maltego] Failed to write XML: {e}")
            raise
