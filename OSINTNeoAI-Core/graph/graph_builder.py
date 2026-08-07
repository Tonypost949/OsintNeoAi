from .schema import GraphSchema

class GraphBuilder:
    """Graph construction utility converting tables into Cypher queries and node dictionaries."""
    
    def __init__(self, neo4j_driver=None):
        self.driver = neo4j_driver

    def build_node_query(self, node_type, properties):
        """Generates a Cypher merge query for a node, enforcing schema labels."""
        if not GraphSchema.validate_node(node_type):
            raise ValueError(f"Invalid graph node label under current schema constraints: {node_type}")
            
        # Clean property dictionary keys
        clean_props = {str(k).replace(" ", "_"): v for k, v in properties.items() if v is not None}
        
        # We merge on a unique identifier, assume 'id' or fallback to the first property
        key_prop = "id" if "id" in clean_props else list(clean_props.keys())[0]
        
        set_statements = ", ".join([f"n.{k} = ${k}" for k in clean_props.keys()])
        query = f"MERGE (n:{node_type} {{{key_prop}: ${key_prop}}}) ON CREATE SET {set_statements} ON MATCH SET {set_statements} RETURN n"
        
        return query, clean_props

    def build_relationship_query(self, source_type, source_id, rel_type, target_type, target_id):
        """Generates a Cypher merge query for a relationship, enforcing schema constraints."""
        if not GraphSchema.validate_node(source_type) or not GraphSchema.validate_node(target_type):
            raise ValueError("Source or Target node label violates schema.")
            
        if not GraphSchema.validate_relationship(rel_type):
            raise ValueError(f"Relationship type '{rel_type}' is not recognized by the graph schema.")
            
        query = (
            f"MATCH (s:{source_type} {{id: $source_id}}), (t:{target_type} {{id: $target_id}}) "
            f"MERGE (s)-[r:{rel_type}]->(t) "
            f"RETURN r"
        )
        params = {
            "source_id": source_id,
            "target_id": target_id
        }
        return query, params

    def load_dataframe_to_neo4j(self, df, node_type, mapping_func):
        """Iterates through a pandas dataframe, compiles nodes/relationships, and commits to Neo4j."""
        if not self.driver:
            print("[Graph] Neo4j driver not attached; writing Cypher commands to offline logs instead.")
            
        cypher_queries = []
        for idx, row in df.iterrows():
            try:
                node_data = mapping_func(row)
                if not node_data:
                    continue
                    
                q, params = self.build_node_query(node_type, node_data)
                cypher_queries.append((q, params))
                
                if self.driver:
                    with self.driver.session() as session:
                        session.run(q, **params)
            except Exception as e:
                print(f"[Graph] Error building node at index {idx}: {e}")
                
        return cypher_queries
