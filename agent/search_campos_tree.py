import pandas as pd

def search_campos_network():
    print("--- Searching PPP Loans ---")
    try:
        ppp = pd.read_csv('bq_board_ppp_final.csv')
        # El Paso + Campos
        el_paso_campos = ppp[ppp['BorrowerName'].str.contains('CAMPOS', na=False, case=False) & 
                             ppp['BorrowerCity'].str.contains('EL PASO', na=False, case=False)]
        print(f"El Paso PPP Campos hits: {len(el_paso_campos)}")
        if not el_paso_campos.empty:
            print(el_paso_campos[['BorrowerName', 'BorrowerCity', 'BorrowerState']])
            
        # Gloria Campos
        gloria = ppp[ppp['BorrowerName'].str.contains('GLORIA CAMPOS', na=False, case=False)]
        print(f"\nGloria Campos PPP hits: {len(gloria)}")
        if not gloria.empty:
            print(gloria[['BorrowerName', 'BorrowerCity', 'BorrowerState']])
            
        # Drew / Andrew in Huntington Beach
        hb_andrew = ppp[ppp['BorrowerName'].str.contains('ANDREW CAMPOS|DREW CAMPOS', na=False, case=False) & 
                        ppp['BorrowerCity'].str.contains('HUNTINGTON BEACH', na=False, case=False)]
        print(f"\nHB Andrew/Drew Campos PPP hits: {len(hb_andrew)}")
        
    except Exception as e:
        print(f"PPP Error: {e}")

    print("\n--- Searching Tribal Unclaimed Matches ---")
    try:
        tribal = pd.read_csv('tribal_unclaimed_matches.csv')
        # Gloria
        gloria_t = tribal[tribal['decedent_or_heir_name'].str.contains('GLORIA CAMPOS', na=False, case=False)]
        print(f"Gloria Campos Tribal hits: {len(gloria_t)}")
        if not gloria_t.empty:
            print(gloria_t[['decedent_or_heir_name', 'county', 'amount_1']])
            
        # Frankie / Simon
        frankie_simon = tribal[tribal['decedent_or_heir_name'].str.contains('FRANKIE CAMPOS|SIMON CAMPOS', na=False, case=False)]
        print(f"\nFrankie/Simon Campos Tribal hits: {len(frankie_simon)}")
        if not frankie_simon.empty:
            print(frankie_simon[['decedent_or_heir_name', 'county', 'amount_1']])
            
        # El Paso is not typically in CA state controller db, but we can check address if we had it.
    except Exception as e:
        print(f"Tribal Error: {e}")

if __name__ == '__main__':
    search_campos_network()
