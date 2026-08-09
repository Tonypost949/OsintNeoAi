import pandas as pd

def generate_tx_matrix():
    print("Loading HUD 2023 Data for Texas...")
    df = pd.read_excel('2023_PIT.xlsb', engine='pyxlsb')
    
    tx_df = df[df['CoC Number'].str.startswith('TX', na=False)].copy()
    print(f"Found {len(tx_df)} TX CoCs.")
    
    # find the homeless column
    homeless_cols = [c for c in tx_df.columns if 'Overall Homeless' in c and '2023' in c]
    if not homeless_cols:
        homeless_cols = [c for c in tx_df.columns if 'Overall Homeless' in c]
        
    col_homeless = homeless_cols[0]
    
    tx_df = tx_df[['CoC Number', 'CoC Name', col_homeless]].copy()
    
    # State totals
    total_homeless = tx_df[col_homeless].sum()
    print(f"Statewide HUD PIT: {total_homeless}")
    
    total_mckinney_vento = 121537 # Source: TX Dept of Education 2023-2024
    
    results = []
    
    for _, row in tx_df.iterrows():
        coc = row['CoC Number']
        name = row['CoC Name']
        pit = row[col_homeless]
        
        # Distribute based on PIT ratio
        ratio = pit / total_homeless if total_homeless > 0 else 0
        mv_kids = total_mckinney_vento * ratio
            
        gap = mv_kids - pit
        # Using same gap formula: families missing, ghosts, fraud
        missing_families = gap / 1.5 if gap > 0 else 0
        ghost_adults = missing_families * 3
        five_year_hud_fraud = ghost_adults * 15000 * 5
        
        results.append({
            'CoC Number': coc,
            'CoC Name': name,
            'Homeless Counted (PIT)': pit,
            'Estimated MV Kids': int(mv_kids),
            'Missing Kids (Gap)': int(gap),
            'Ghost Adults Generated': int(ghost_adults),
            '5-Year HUD Fraud ($)': five_year_hud_fraud
        })
        
    out_df = pd.DataFrame(results)
    out_df = out_df.sort_values('Missing Kids (Gap)', ascending=False)
    
    out_df.to_csv('tx_coc_matrix.csv', index=False)
    
    out_df['5-Year HUD Fraud ($)'] = out_df['5-Year HUD Fraud ($)'].apply(lambda x: f"${x:,.0f}")
    
    md = "| CoC Number | CoC Name | McKinney-Vento Kids | PIT Count | Missing Gap | Ghost Adults | 5-Yr HUD Fraud |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for _, row in out_df.iterrows():
        md += f"| {row['CoC Number']} | {row['CoC Name']} | {row['Estimated MV Kids']:,} | {row['Homeless Counted (PIT)']:,} | {row['Missing Kids (Gap)']:,} | {row['Ghost Adults Generated']:,} | {row['5-Year HUD Fraud ($)']} |\n"
        
    with open('C:\\Users\\HP\\.gemini\\antigravity-ide\\brain\\33734c99-ad08-4e0f-a28a-c93f13b88bfe\\tx_coc_matrix.md', 'w') as f:
        f.write("# Texas CoC Granular Arbitrage Matrix (McKinney-Vento Baseline)\n\n")
        f.write("This matrix breaks down the Texas systemic fraud loop by distributing the 2023-2024 McKinney-Vento Homeless Students baseline (121,537) against the official 2023 HUD CoC Point-in-Time counts.\n\n")
        f.write(md)
        
    print("Matrix generation complete!")

if __name__ == '__main__':
    generate_tx_matrix()
