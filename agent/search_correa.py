import pandas as pd

def search_correa_santa_maria():
    print("--- Searching PPP Loans ---")
    try:
        ppp = pd.read_csv('bq_board_ppp_final.csv')
        
        # Correa
        correa = ppp[ppp['BorrowerName'].str.contains('SYLVIA CORREA| CORREA', na=False, case=False)]
        print(f"Sylvia / Correa PPP hits: {len(correa)}")
        if not correa.empty:
            print(correa[['BorrowerName', 'BorrowerCity', 'BorrowerState']].head(5))
            
        # Santa Maria + Campos
        sm_campos = ppp[ppp['BorrowerName'].str.contains('CAMPOS', na=False, case=False) & 
                        ppp['BorrowerCity'].str.contains('SANTA MARIA', na=False, case=False)]
        print(f"\nSanta Maria Campos PPP hits: {len(sm_campos)}")
        if not sm_campos.empty:
            print(sm_campos[['BorrowerName', 'BorrowerCity', 'BorrowerState']])
            
    except Exception as e:
        print(f"PPP Error: {e}")

    print("\n--- Searching Tribal Unclaimed Matches ---")
    try:
        tribal = pd.read_csv('tribal_unclaimed_matches.csv')
        
        # Correa
        correa_t = tribal[tribal['decedent_or_heir_name'].str.contains('SYLVIA CORREA| CORREA', na=False, case=False)]
        print(f"Correa Tribal hits: {len(correa_t)}")
        if not correa_t.empty:
            print(correa_t[['decedent_or_heir_name', 'county', 'amount_1']].head(5))
            
    except Exception as e:
        print(f"Tribal Error: {e}")

if __name__ == '__main__':
    search_correa_santa_maria()
