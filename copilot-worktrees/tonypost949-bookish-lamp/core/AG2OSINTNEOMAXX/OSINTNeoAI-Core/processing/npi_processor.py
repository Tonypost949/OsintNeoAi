import os
import pandas as pd

class NPIProcessor:
    """NPI (NPPES) and IRS EIN data cross-referencing and cleaning processor."""
    
    def __init__(self, npi_export_path=None):
        self.npi_export_path = npi_export_path

    def load_npi_data(self, file_path=None):
        """Loads and parses raw NPPES provider datasets."""
        target_path = file_path or self.npi_export_path
        if not target_path or not os.path.exists(target_path):
            print(f"[NPI] NPI export path not found: {target_path}")
            return pd.DataFrame()
            
        try:
            # NPPES records are usually large, read selectively
            df = pd.read_csv(target_path, dtype=str, nrows=50000)
            print(f"[NPI] Loaded {len(df)} NPI directory records.")
            return df
        except Exception as e:
            print(f"[NPI] Error loading NPI file {target_path}: {e}")
            return pd.DataFrame()

    def filter_by_ein(self, npi_df, ein_list):
        """Filter provider listings matching a specific checklist of IRS Employer Identification Numbers (EINs)."""
        if npi_df.empty or not ein_list:
            return pd.DataFrame()
            
        # Common NPPES field names for employer numbers
        ein_columns = [col for col in npi_df.columns if 'ein' in col.lower() or 'employer' in col.lower()]
        if not ein_columns:
            print("[NPI] No EIN/Employer identifier columns found in NPI dataframe.")
            return pd.DataFrame()
            
        ein_set = set(str(e).strip() for e in ein_list)
        mask = npi_df[ein_columns].apply(lambda row: any(str(val).strip() in ein_set for val in row), axis=1)
        
        filtered_df = npi_df[mask]
        print(f"[NPI] Identified {len(filtered_df)} matches against {len(ein_list)} target EIN dockets.")
        return filtered_df

    def clean_provider_names(self, npi_df):
        """Standardizes provider first/last names and entity corporate identifiers."""
        if npi_df.empty:
            return npi_df
            
        df = npi_df.copy()
        # Clean Organization Names
        if 'Provider Organization Name (Legal Business Name)' in df.columns:
            df['clean_org_name'] = df['Provider Organization Name (Legal Business Name)'].str.strip().str.upper()
            
        # Clean Individual Names
        if 'Provider First Name' in df.columns and 'Provider Last Name' in df.columns:
            df['clean_individual_name'] = (
                df['Provider First Name'].str.strip().str.upper() + " " + 
                df['Provider Last Name'].str.strip().str.upper()
            )
            
        return df
