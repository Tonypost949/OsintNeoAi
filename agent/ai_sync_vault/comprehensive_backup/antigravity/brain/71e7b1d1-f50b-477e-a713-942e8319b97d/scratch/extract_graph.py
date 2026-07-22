import os
import csv
import json
import re
import ast

class GraphSchema:
    NODE_PERSON = "PERSON"
    NODE_ORGANIZATION = "ORGANIZATION"
    NODE_ADDRESS = "ADDRESS"
    NODE_PROPERTY = "PROPERTY"
    NODE_PPP_LOAN = "PPP_LOAN"
    NODE_CASE = "CASE"
    NODE_ATTORNEY = "ATTORNEY"
    NODE_STATE = "STATE"
    NODE_ARTICLE = "ARTICLE"
    
    NODE_TYPES = {
        NODE_PERSON, NODE_ORGANIZATION, NODE_ADDRESS, 
        NODE_PROPERTY, NODE_PPP_LOAN, NODE_CASE, 
        NODE_ATTORNEY, NODE_STATE, NODE_ARTICLE
    }
    
    REL_OWNS = "OWNS"
    REL_RECEIVED_PPP = "RECEIVED_PPP"
    REL_REGISTERED_AT = "REGISTERED_AT"
    REL_LOCATED_IN = "LOCATED_IN"
    REL_OFFICER_OF = "OFFICER_OF"
    REL_DIRECTOR_OF = "DIRECTOR_OF"
    REL_LITIGANT_IN = "LITIGANT_IN"
    REL_REPRESENTED_BY = "REPRESENTED_BY"
    REL_CONNECTED_TO = "CONNECTED_TO"
    
    RELATIONSHIP_TYPES = {
        REL_OWNS, REL_RECEIVED_PPP, REL_REGISTERED_AT,
        REL_LOCATED_IN, REL_OFFICER_OF, REL_DIRECTOR_OF,
        REL_LITIGANT_IN, REL_REPRESENTED_BY, REL_CONNECTED_TO
    }

class ComprehensiveGraphExtractor:
    ORG_SUFFIX_REGEX = re.compile(
        r"\b(LLC|INC|CORP|CO|LTD|PARTNERSHIP|LP|MHC|TRUST|ASSOCIATES|HOLDINGS|INVESTMENTS|PROPERTIES|GROUP|CAPITAL|MANAGEMENT|ENTERPRISES|CHURCH|COMMUNITY|FOUNDATION|SOCIETY|CORPORTATION|CITY|COUNTY|STATE|DEPARTMENT|AUTHORITY|AGENCY)\b",
        re.IGNORECASE
    )

    def __init__(self):
        self.nodes = {}
        self.edges = []
        
    def clean_str(self, val):
        if not val or str(val).strip().upper() in ("NULL", "N/A", "NONE", ""):
            return ""
        return str(val).strip().strip(",").strip().upper()

    def resolve_entity_type(self, name):
        cleaned = self.clean_str(name)
        if not cleaned:
            return ""
        if self.ORG_SUFFIX_REGEX.search(cleaned):
            return GraphSchema.NODE_ORGANIZATION
        return GraphSchema.NODE_PERSON

    def parse_individual_names(self, name_str):
        if not name_str:
            return []
        parts = re.split(r'[;;&]', str(name_str))
        return [self.clean_str(part) for part in parts if self.clean_str(part)]

    def add_node(self, label, node_id, properties):
        if not node_id:
            return
        node_id = self.clean_str(node_id)
        if node_id in self.nodes:
            self.nodes[node_id]["properties"].update(properties)
        else:
            self.nodes[node_id] = {
                "id": node_id,
                "label": label,
                "properties": properties
            }

    def add_edge(self, source_id, source_label, rel_type, target_id, target_label, properties=None):
        if not source_id or not target_id:
            return
        self.edges.append({
            "source_id": self.clean_str(source_id),
            "source_label": source_label,
            "type": rel_type,
            "target_id": self.clean_str(target_id),
            "target_label": target_label,
            "properties": properties or {}
        })

    def extract_from_out_of_state_llc_ppp_network(self, filepath):
        if not os.path.exists(filepath):
            return
        
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                owner_name = self.clean_str(row.get("owner_name", ""))
                prop_addr = self.clean_str(row.get("property_address", ""))
                apn = self.clean_str(row.get("apn", ""))
                last_sale_val = self.clean_str(row.get("last_sale_value", ""))
                last_sale_date = self.clean_str(row.get("last_sale_date", ""))
                mail_addr = self.clean_str(row.get("property_mail_address", ""))
                mail_city = self.clean_str(row.get("property_mail_city", ""))
                
                ppp_loan_count = self.clean_str(row.get("ppp_loan_count", ""))
                ppp_total_amount = self.clean_str(row.get("ppp_total_amount", ""))
                ppp_total_forgiven = self.clean_str(row.get("ppp_total_forgiven", ""))
                ppp_names = self.clean_str(row.get("ppp_names", ""))
                loan_locations = self.clean_str(row.get("loan_locations", ""))
                loan_statuses = self.clean_str(row.get("loan_statuses", ""))

                # Resolve owner
                owner_label = self.resolve_entity_type(owner_name)
                self.add_node(owner_label, owner_name, {"name": owner_name})

                # Resolve property
                if apn:
                    prop_props = {"apn": apn}
                    if last_sale_val: prop_props["last_sale_value"] = last_sale_val
                    if last_sale_date: prop_props["last_sale_date"] = last_sale_date
                    self.add_node(GraphSchema.NODE_PROPERTY, apn, prop_props)
                    self.add_edge(owner_name, owner_label, GraphSchema.REL_OWNS, apn, GraphSchema.NODE_PROPERTY)

                # Resolve property address (Site)
                if prop_addr:
                    self.add_node(GraphSchema.NODE_ADDRESS, prop_addr, {"address": prop_addr, "type": "SITE"})
                    if apn:
                        self.add_edge(apn, GraphSchema.NODE_PROPERTY, GraphSchema.REL_LOCATED_IN, prop_addr, GraphSchema.NODE_ADDRESS)

                # Resolve property mailing address
                mail_id = f"{mail_addr}, {mail_city}" if mail_addr and mail_city else mail_addr
                if mail_id:
                    self.add_node(GraphSchema.NODE_ADDRESS, mail_id, {"address": mail_addr, "city": mail_city, "type": "MAILING"})
                    self.add_edge(owner_name, owner_label, GraphSchema.REL_REGISTERED_AT, mail_id, GraphSchema.NODE_ADDRESS)

                # Extract PPP loan if any
                try:
                    amount_val = float(ppp_total_amount) if ppp_total_amount else 0.0
                except ValueError:
                    amount_val = 0.0

                if amount_val > 0 or ppp_loan_count:
                    loan_id = f"PPP_LOAN_{owner_name}"
                    loan_props = {
                        "borrower_name": owner_name,
                        "amount": ppp_total_amount,
                        "forgiven_amount": ppp_total_forgiven,
                        "loan_count": ppp_loan_count,
                        "status": loan_statuses,
                        "location": loan_locations,
                        "ppp_name_listed": ppp_names
                    }
                    self.add_node(GraphSchema.NODE_PPP_LOAN, loan_id, loan_props)
                    self.add_edge(owner_name, owner_label, GraphSchema.REL_RECEIVED_PPP, loan_id, GraphSchema.NODE_PPP_LOAN)

    def extract_from_national_audits_all_state_records(self, filepath):
        if not os.path.exists(filepath):
            return
        
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                state_code = self.clean_str(row.get("state", ""))
                if not state_code:
                    continue
                
                # Add STATE Node
                self.add_node(GraphSchema.NODE_STATE, state_code, {"state_code": state_code})
                
                # Parse HUD PIT List (CoC continuums)
                hud_pit_raw = row.get("hud_pit_list", "[]")
                try:
                    # JSON / Safe Eval parsing
                    coc_data = []
                    if hud_pit_raw.strip().startswith("["):
                        try:
                            coc_data = json.loads(hud_pit_raw.replace("'", '"'))
                        except Exception:
                            try:
                                coc_data = ast.literal_eval(hud_pit_raw)
                            except Exception:
                                pass
                                
                    for coc in coc_data:
                        coc_name = self.clean_str(coc.get("coc_name", ""))
                        coc_number = self.clean_str(coc.get("coc_number", ""))
                        total_homeless = coc.get("total_homeless", "")
                        
                        if coc_name:
                            self.add_node(GraphSchema.NODE_ORGANIZATION, coc_name, {
                                "name": coc_name,
                                "coc_number": coc_number,
                                "total_homeless": total_homeless
                            })
                            # Link Organization CoC to the State
                            self.add_edge(coc_name, GraphSchema.NODE_ORGANIZATION, GraphSchema.REL_LOCATED_IN, state_code, GraphSchema.NODE_STATE)
                except Exception as e:
                    pass

    def extract_from_hb_suspicious_llc_matrix(self, filepath):
        if not os.path.exists(filepath):
            return
        
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                owner1_raw = row.get("Owner1", "")
                owner2_raw = row.get("Owner2", "")
                site_addr = self.clean_str(row.get("SiteAddress", ""))
                mail_addr = self.clean_str(row.get("MailAddress", ""))
                mail_city = self.clean_str(row.get("MailCity", ""))
                apn = self.clean_str(row.get("APN", ""))
                seller_raw = row.get("LastSeller", "")
                sale_date = self.clean_str(row.get("LastSaleDate", ""))
                sale_val = self.clean_str(row.get("LastSaleValue", ""))

                # Resolve property
                if apn:
                    prop_props = {"apn": apn}
                    if sale_date: prop_props["last_sale_date"] = sale_date
                    if sale_val: prop_props["last_sale_value"] = sale_val
                    self.add_node(GraphSchema.NODE_PROPERTY, apn, prop_props)

                # Site address
                if site_addr:
                    self.add_node(GraphSchema.NODE_ADDRESS, site_addr, {"address": site_addr, "type": "SITE"})
                    if apn:
                        self.add_edge(apn, GraphSchema.NODE_PROPERTY, GraphSchema.REL_LOCATED_IN, site_addr, GraphSchema.NODE_ADDRESS)

                # Mailing Address
                mail_id = f"{mail_addr}, {mail_city}" if mail_addr and mail_city else mail_addr
                if mail_id:
                    self.add_node(GraphSchema.NODE_ADDRESS, mail_id, {"address": mail_addr, "city": mail_city, "type": "MAILING"})

                # Owner1
                for o1 in self.parse_individual_names(owner1_raw):
                    o1_label = self.resolve_entity_type(o1)
                    self.add_node(o1_label, o1, {"name": o1})
                    
                    if apn:
                        self.add_edge(o1, o1_label, GraphSchema.REL_OWNS, apn, GraphSchema.NODE_PROPERTY)
                    if mail_id:
                        self.add_edge(o1, o1_label, GraphSchema.REL_REGISTERED_AT, mail_id, GraphSchema.NODE_ADDRESS)

                    # Owner2 (Officers)
                    for o2 in self.parse_individual_names(owner2_raw):
                        o2_label = self.resolve_entity_type(o2)
                        self.add_node(o2_label, o2, {"name": o2})
                        
                        rel = GraphSchema.REL_CONNECTED_TO
                        if o1_label == GraphSchema.NODE_ORGANIZATION and o2_label == GraphSchema.NODE_PERSON:
                            rel = GraphSchema.REL_OFFICER_OF
                            
                        self.add_edge(o2, o2_label, rel, o1, o1_label)
                        
                        if apn:
                            self.add_edge(o2, o2_label, GraphSchema.REL_OWNS, apn, GraphSchema.NODE_PROPERTY)

                # Historical last seller
                for seller in self.parse_individual_names(seller_raw):
                    seller_label = self.resolve_entity_type(seller)
                    self.add_node(seller_label, seller, {"name": seller})
                    if apn:
                        self.add_edge(seller, seller_label, GraphSchema.REL_CONNECTED_TO, apn, GraphSchema.NODE_PROPERTY, {"role": "PAST_SELLER", "date": sale_date})

    def run_all(self):
        # Paths
        out_of_state_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\out_of_state_llc_ppp_network.csv"
        national_audits_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_all_state_records.csv"
        hb_llc_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\HB_Suspicious_LLC_Matrix.csv"
        
        self.extract_from_out_of_state_llc_ppp_network(out_of_state_path)
        self.extract_from_national_audits_all_state_records(national_audits_path)
        self.extract_from_hb_suspicious_llc_matrix(hb_llc_path)
        
        # Save output files
        output_dir = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
        nodes_file = os.path.join(output_dir, "nodes.json")
        edges_file = os.path.join(output_dir, "edges.json")
        
        node_list = list(self.nodes.values())
        
        with open(nodes_file, 'w', encoding='utf-8') as f:
            json.dump(node_list, f, indent=2)
            
        with open(edges_file, 'w', encoding='utf-8') as f:
            json.dump(self.edges, f, indent=2)
            
        print(f"[!] Extraction complete. Saved to nodes.json and edges.json.")
        
        # Calculate statistics
        total_nodes = len(node_list)
        total_edges = len(self.edges)
        
        node_counts = {}
        for node in node_list:
            lbl = node["label"]
            node_counts[lbl] = node_counts.get(lbl, 0) + 1
            
        edge_counts = {}
        for edge in self.edges:
            t = edge["type"]
            edge_counts[t] = edge_counts.get(t, 0) + 1
            
        print("\n==================== EXTRACTION STATISTICS ====================")
        print(f"Total Nodes: {total_nodes}")
        print(f"Total Edges: {total_edges}")
        print("\nNode Counts by Type:")
        for lbl, count in sorted(node_counts.items()):
            print(f"  - {lbl}: {count}")
            
        print("\nRelationship Counts by Type:")
        for t, count in sorted(edge_counts.items()):
            print(f"  - {t}: {count}")
            
        print("\n==================== 10 REAL EXAMPLE RELATIONSHIPS ====================")
        # Gather samples of different types to show variety
        samples = []
        seen_triples = set()
        
        # Priority patterns: 
        # 1. ORGANIZATION -> RECEIVED_PPP -> PPP_LOAN
        # 2. ORGANIZATION/PERSON -> REGISTERED_AT -> ADDRESS
        # 3. PROPERTY -> LOCATED_IN -> ADDRESS / STATE
        for edge in self.edges:
            triple = (edge["source_label"], edge["type"], edge["target_label"])
            if triple not in seen_triples and len(samples) < 10:
                seen_triples.add(triple)
                samples.append(edge)
                
        # Fill remaining up to 10 with other unique source-target instances
        for edge in self.edges:
            if len(samples) >= 10:
                break
            # Add instance if not already shown as an exact id match
            if not any(s["source_id"] == edge["source_id"] and s["target_id"] == edge["target_id"] for s in samples):
                samples.append(edge)
                
        for idx, edge in enumerate(samples, start=1):
            print(f"{idx}. {edge['source_id']} ({edge['source_label']}) -> {edge['type']} -> {edge['target_id']} ({edge['target_label']})")

if __name__ == "__main__":
    extractor = ComprehensiveGraphExtractor()
    extractor.run_all()

