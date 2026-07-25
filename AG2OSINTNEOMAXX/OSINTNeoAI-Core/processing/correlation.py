import os
import re
import pandas as pd
from datetime import datetime

class AegisCorrelationEngine:
    """Consolidated entity resolution and corporate relationship mapping engine."""
    
    def __init__(self, workspace_path=None):
        self.workspace_path = workspace_path or os.getcwd()
        self.evidence_links = []
        
    def scan_workspace_for_evidence(self):
        """Scans the workspace directory for evidence tables (CSV, JSON, XLSX)."""
        scanned_files = []
        if not os.path.exists(self.workspace_path):
            return scanned_files
            
        for root, dirs, files in os.walk(self.workspace_path):
            for file in files:
                if file.endswith((".json", ".csv", ".xlsx", ".txt")):
                    scanned_files.append(os.path.join(root, file))
        return scanned_files

    def normalize_name(self, name):
        """Normalize person/entity names for high-accuracy fuzzy/exact matches."""
        if not name or pd.isna(name):
            return ""
        name_str = str(name).strip().upper()
        # Strip common suffixes
        name_str = re.sub(r'\b(LLC|INC|CORP|CO|LTD|LP|PLC|GMBH)\b', '', name_str)
        # Strip symbols and extra whitespaces
        name_str = re.sub(r'[^\w\s]', '', name_str)
        return " ".join(name_str.split())

    def match_entities(self, df_a, col_a, df_b, col_b, threshold=0.85):
        """Perform exact and fuzzy matches between two dataframes on specified columns."""
        matches = []
        
        # Exact Matching on Normalized Names
        norm_a = df_a[col_a].apply(self.normalize_name)
        norm_b = df_b[col_b].apply(self.normalize_name)
        
        for idx_a, val_a in norm_a.items():
            if not val_a:
                continue
            # Simple substring matching
            for idx_b, val_b in norm_b.items():
                if not val_b:
                    continue
                if val_a == val_b or (len(val_a) > 4 and (val_a in val_b or val_b in val_a)):
                    matches.append({
                        "source_index": idx_a,
                        "target_index": idx_b,
                        "source_value": df_a.loc[idx_a, col_a],
                        "target_value": df_b.loc[idx_b, col_b],
                        "match_type": "EXACT" if val_a == val_b else "SUBSTRING",
                        "timestamp": datetime.utcnow().isoformat()
                    })
        return pd.DataFrame(matches)

    def parse_workbook_entities(self, xlsx_path):
        """Parse structured workbook excel sheets and map standard columns."""
        if not os.path.exists(xlsx_path):
            raise FileNotFoundError(f"Workbook not found: {xlsx_path}")
            
        workbook_data = {}
        try:
            excel_file = pd.ExcelFile(xlsx_path)
            for sheet_name in excel_file.sheet_names:
                df = excel_file.parse(sheet_name)
                workbook_data[sheet_name] = df
        except Exception as e:
            print(f"[Aegis] Error parsing workbook {xlsx_path}: {e}")
            
        return workbook_data
