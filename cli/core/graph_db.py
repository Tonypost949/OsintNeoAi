import json
import os
import uuid

class GraphDB:
    def __init__(self, db_file="data/graph.json"):
        self.db_file = db_file
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump({"nodes": [], "links": []}, f)
        
        self.load()

    def load(self):
        with open(self.db_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def add_entity(self, entity_type, value):
        # Check if node already exists by value
        for node in self.data["nodes"]:
            if node["value"] == value:
                return node["id"]
        
        node_id = str(uuid.uuid4())
        self.data["nodes"].append({
            "id": node_id,
            "type": entity_type,
            "value": value
        })
        self.save()
        return node_id

    def add_relation(self, source_id, target_id, label=""):
        # Check if link exists
        for link in self.data["links"]:
            if link["source"] == source_id and link["target"] == target_id:
                return
        
        self.data["links"].append({
            "source": source_id,
            "target": target_id,
            "label": label
        })
        self.save()

    def delete_entity(self, entity_id):
        node_exists = any(n["id"] == entity_id for n in self.data["nodes"])
        if not node_exists:
            return False

        # Remove node
        self.data["nodes"] = [n for n in self.data["nodes"] if n["id"] != entity_id]
        # Remove attached links
        self.data["links"] = [l for l in self.data["links"] if l["source"] != entity_id and l["target"] != entity_id]
        
        self.save()
        return True
