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
    NODE_STATE = "STATE"
    
    NODE_TYPES = {NODE_PERSON, NODE_ORGANIZATION, NODE_ADDRESS, NODE_PROPERTY, NODE_PPP_LOAN, NODE_STATE}
    
    REL_OWNS = "OWNS"
    REL_RECEIVED_PPP = "RECEIVED_PPP"
    REL_REGISTERED_AT = "REGISTERED_AT"
    REL_LOCATED_IN = "LOCATED_IN"
    REL_OFFICER_OF = "OFFICER_OF"
    REL_CONNECTED_TO = "CONNECTED_TO"

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

                owner_label = self.resolve_entity_type(owner_name)
                self.add_node(owner_label, owner_name, {"name": owner_name})

                if apn:
                    prop_props = {"apn": apn}
                    if last_sale_val: prop_props["last_sale_value"] = last_sale_val
                    if last_sale_date: prop_props["last_sale_date"] = last_sale_date
                    self.add_node(GraphSchema.NODE_PROPERTY, apn, prop_props)
                    self.add_edge(owner_name, owner_label, GraphSchema.REL_OWNS, apn, GraphSchema.NODE_PROPERTY)

                if prop_addr:
                    self.add_node(GraphSchema.NODE_ADDRESS, prop_addr, {"address": prop_addr, "type": "SITE"})
                    if apn:
                        self.add_edge(apn, GraphSchema.NODE_PROPERTY, GraphSchema.REL_LOCATED_IN, prop_addr, GraphSchema.NODE_ADDRESS)

                mail_id = f"{mail_addr}, {mail_city}" if mail_addr and mail_city else mail_addr
                if mail_id:
                    self.add_node(GraphSchema.NODE_ADDRESS, mail_id, {"address": mail_addr, "city": mail_city, "type": "MAILING"})
                    self.add_edge(owner_name, owner_label, GraphSchema.REL_REGISTERED_AT, mail_id, GraphSchema.NODE_ADDRESS)

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
                
                self.add_node(GraphSchema.NODE_STATE, state_code, {"state_code": state_code})
                
                hud_pit_raw = row.get("hud_pit_list", "[]")
                try:
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
                            self.add_edge(coc_name, GraphSchema.NODE_ORGANIZATION, GraphSchema.REL_LOCATED_IN, state_code, GraphSchema.NODE_STATE)
                except Exception:
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

                if apn:
                    prop_props = {"apn": apn}
                    if sale_date: prop_props["last_sale_date"] = sale_date
                    if sale_val: prop_props["last_sale_value"] = sale_val
                    self.add_node(GraphSchema.NODE_PROPERTY, apn, prop_props)

                if site_addr:
                    self.add_node(GraphSchema.NODE_ADDRESS, site_addr, {"address": site_addr, "type": "SITE"})
                    if apn:
                        self.add_edge(apn, GraphSchema.NODE_PROPERTY, GraphSchema.REL_LOCATED_IN, site_addr, GraphSchema.NODE_ADDRESS)

                mail_id = f"{mail_addr}, {mail_city}" if mail_addr and mail_city else mail_addr
                if mail_id:
                    self.add_node(GraphSchema.NODE_ADDRESS, mail_id, {"address": mail_addr, "city": mail_city, "type": "MAILING"})

                for o1 in self.parse_individual_names(owner1_raw):
                    o1_label = self.resolve_entity_type(o1)
                    self.add_node(o1_label, o1, {"name": o1})
                    
                    if apn:
                        self.add_edge(o1, o1_label, GraphSchema.REL_OWNS, apn, GraphSchema.NODE_PROPERTY)
                    if mail_id:
                        self.add_edge(o1, o1_label, GraphSchema.REL_REGISTERED_AT, mail_id, GraphSchema.NODE_ADDRESS)

                    for o2 in self.parse_individual_names(owner2_raw):
                        o2_label = self.resolve_entity_type(o2)
                        self.add_node(o2_label, o2, {"name": o2})
                        
                        rel = GraphSchema.REL_CONNECTED_TO
                        if o1_label == GraphSchema.NODE_ORGANIZATION and o2_label == GraphSchema.NODE_PERSON:
                            rel = GraphSchema.REL_OFFICER_OF
                            
                        self.add_edge(o2, o2_label, rel, o1, o1_label)
                        
                        if apn:
                            self.add_edge(o2, o2_label, GraphSchema.REL_OWNS, apn, GraphSchema.NODE_PROPERTY)

                for seller in self.parse_individual_names(seller_raw):
                    seller_label = self.resolve_entity_type(seller)
                    self.add_node(seller_label, seller, {"name": seller})
                    if apn:
                        self.add_edge(seller, seller_label, GraphSchema.REL_CONNECTED_TO, apn, GraphSchema.NODE_PROPERTY, {"role": "PAST_SELLER", "date": sale_date})

    def extract_from_us_coc_pattern_master(self, filepath):
        if not os.path.exists(filepath):
            return
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line.startswith("|"):
                    continue
                parts = [p.strip() for p in line.split("|")]
                if len(parts) < 9:
                    continue
                state_code = parts[1].replace("**", "").replace("*", "").strip().upper()
                coc_number = parts[2].replace("**", "").replace("*", "").strip().upper()
                coc_name = parts[3].replace("**", "").replace("*", "").strip()
                counties_covered = parts[4].strip()
                policing_status = parts[5].strip()
                ej_flag = parts[6].strip()
                mercy_house = parts[7].strip()
                notes = parts[8].strip()
                
                if state_code == "STATE" or "---" in state_code or not state_code:
                    continue
                if coc_number == "COC NUMBER" or "---" in coc_number:
                    continue
                
                state_code = self.clean_str(state_code)
                coc_name_clean = self.clean_str(coc_name)
                
                if state_code:
                    self.add_node(GraphSchema.NODE_STATE, state_code, {"state_code": state_code})
                
                if coc_name_clean:
                    self.add_node(GraphSchema.NODE_ORGANIZATION, coc_name_clean, {
                        "name": coc_name,
                        "coc_number": coc_number,
                        "counties_covered": counties_covered,
                        "policing_status": policing_status,
                        "environmental_justice_flag": ej_flag,
                        "mercy_house_presence": mercy_house,
                        "operational_notes": notes
                    })
                    if state_code:
                        self.add_edge(coc_name_clean, GraphSchema.NODE_ORGANIZATION, GraphSchema.REL_LOCATED_IN, state_code, GraphSchema.NODE_STATE)

    def run_all(self):
        out_of_state_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\out_of_state_llc_ppp_network.csv"
        national_audits_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_all_state_records.csv"
        hb_llc_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\HB_Suspicious_LLC_Matrix.csv"
        us_coc_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\us_coc_forensic_pattern_master.md"
        
        self.extract_from_out_of_state_llc_ppp_network(out_of_state_path)
        self.extract_from_national_audits_all_state_records(national_audits_path)
        self.extract_from_hb_suspicious_llc_matrix(hb_llc_path)
        self.extract_from_us_coc_pattern_master(us_coc_path)
        
        output_dir = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
        nodes_path = os.path.join(output_dir, "nodes.json")
        edges_path = os.path.join(output_dir, "edges.json")
        
        with open(nodes_path, 'w', encoding='utf-8') as f:
            json.dump(list(self.nodes.values()), f, indent=2)
        with open(edges_path, 'w', encoding='utf-8') as f:
            json.dump(self.edges, f, indent=2)
            
        print("[!] Saved to nodes.json and edges.json successfully.")

if __name__ == "__main__":
    extractor = ComprehensiveGraphExtractor()
    extractor.run_all()
