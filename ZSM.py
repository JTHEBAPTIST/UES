import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore

# ---------------------------------------------------------
# Part 1: Preparation of Data
# ---------------------------------------------------------

st.title('Multi-factor Model Data Processor')

# File uploader
uploaded_file = st.file_uploader("Please upload your Excel or CSV file:", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Reading input data based on file type
    file_extension = uploaded_file.name.split('.')[-1]
    
    if file_extension == 'csv':
        in_data = pd.read_csv(uploaded_file, header=3, delimiter='\t')
    elif file_extension == 'xlsx':
        in_data = pd.read_excel(uploaded_file, header=3)
    else:
        st.error("Unsupported file format. Please upload an Excel or CSV file.")
        st.stop()
    
    st.write("File uploaded successfully.")

    # Filter stocks where 'In Buy List' > 0
    if 'In Buy List' in in_data.columns:
        data = in_data[in_data['In Buy List'] > 0]
    else:
        st.error("'In Buy List' column not found in uploaded file.")
        st.stop()

    # Print columns to verify correct loading
    st.write("Columns available in the DataFrame:")
    st.write(data.columns.tolist())

    # Define function to pull Z-score data for specified factors
    def extract_factor_scores(df):
        # List of factors with columns to pull scores from
        factors = [
            {'output_col': 'Value', 'columns': ['Value Score (IQR)', 'Value Score (W)']},
            {'output_col': 'Momentum', 'columns': ['Momentum Score (IQR)', 'Momentum Score (W)']},
            {'output_col': 'PEG', 'columns': ['PEG Score (IQR)', 'PEG Score (W)']},
            {'output_col': 'Earnings Surprise', 'columns': ['Earnings Surprise Score (IQR)', 'Earnings Surprise Score (W)']},
            {'output_col': 'ROE', 'columns': ['Ret on Avg Total Equity (IQR)', 'Ret on Avg Total Equity (W)']},
            {'output_col': 'ROA', 'columns': ['Ret on Avg Total Assets (IQR)', 'Ret on Avg Total Assets (W)']},
            {'output_col': 'Net Profit Margin', 'columns': ['Net Income Margin (IQR)', 'Net Income Margin (W)']},
            {'output_col': '5Y Growth Gross Profit', 'columns': ['Chg in GP/Sales Score (IQR)', 'Chg in GP/Sales Score (W)']},
            {'output_col': '5Y NI-BV Growth', 'columns': ['Chg in NI/BV Score (IQR)', 'Chg in NI/BV Score (W)']},
            {'output_col': '5Y NI-Asset Growth', 'columns': ['Chg in NI/Assets Score (IQR)', 'Chg in NI/Assets Score (W)']},
            {'output_col': 'Dividend Payout Ratio', 'columns': ['Div Pd Score (IQR)', 'Div Pd Score (W)']},
            {'output_col': 'Pct Change Shares Outstanding', 'columns': ['Chg Shs Outstdg Score (IQR)', 'Chg Shs Outstdg Score (W)']},
            {'output_col': 'Debt-to-Equity', 'columns': ['D/E Score (IQR)', 'D/E Score (W)']},
            {'output_col': 'Pre-tax Interest Coverage', 'columns': ['PreTax Int Cov Score (IQR)', 'PreTax Int Cov Score (W)']},
            {'output_col': 'Accruals', 'columns': ['Norm Accrual Score (IQR)', 'Norm Accrual Score (W)']},
            {'output_col': 'Beta', 'columns': ['Norm Beta (IQR)', 'Norm Beta (W)']},
            {'output_col': 'Final Model Score', 'columns': ['Final Model Score (IQR)', 'Final Model Score (W)']}
        ]
        
        # Loop through factors and assign scores based on availability
        for factor in factors:
            output_col = factor['output_col']
            col_IQR, col_W = factor['columns']
            # Use IQR score if available, otherwise use W score
            df[output_col] = df.get(col_IQR, np.nan).combine_first(df.get(col_W, np.nan))
        
        return df

    # Process data to extract the Z-score model data
    data = extract_factor_scores(data)

    # ---------------------------------------------------------
    # Part 2: Calculating Z-scores for Each Factor
    # ---------------------------------------------------------

    def calculate_z_scores(df):
        factors = [
            {'output_col': 'Value', 'columns': ['Value Score (IQR)', 'Value Score (W)']},
            {'output_col': 'Momentum', 'columns': ['Momentum Score (IQR)', 'Momentum Score (W)']},
            {'output_col': 'PEG', 'columns': ['PEG Score (IQR)', 'PEG Score (W)']},
            {'output_col': 'Earnings Surprise', 'columns': ['Earnings Surprise Score (IQR)', 'Earnings Surprise Score (W)']},
            {'output_col': 'ROE', 'columns': ['Ret on Avg Total Equity (IQR)', 'Ret on Avg Total Equity (W)']},
            {'output_col': 'ROA', 'columns': ['Ret on Avg Total Assets (IQR)', 'Ret on Avg Total Assets (W)']},
            {'output_col': 'Net Profit Margin', 'columns': ['Net Income Margin (IQR)', 'Net Income Margin (W)']},
            {'output_col': '5Y Growth Gross Profit', 'columns': ['Chg in GP/Sales Score (IQR)', 'Chg in GP/Sales Score (W)']},
            {'output_col': '5Y NI-BV Growth', 'columns': ['Chg in NI/BV Score (IQR)', 'Chg in NI/BV Score (W)']},
            {'output_col': '5Y NI-Asset Growth', 'columns': ['Chg in NI/Assets Score (IQR)', 'Chg in NI/Assets Score (W)']},
            {'output_col': 'Dividend Payout Ratio', 'columns': ['Div Pd Score (IQR)', 'Div Pd Score (W)']},
            {'output_col': 'Pct Change Shares Outstanding', 'columns': ['Chg Shs Outstdg Score (IQR)', 'Chg Shs Outstdg Score (W)']},
            {'output_col': 'Debt-to-Equity', 'columns': ['D/E Score (IQR)', 'D/E Score (W)']},
            {'output_col': 'Pre-tax Interest Coverage', 'columns': ['PreTax Int Cov Score (IQR)', 'PreTax Int Cov Score (W)']},
            {'output_col': 'Accruals', 'columns': ['Norm Accrual Score (IQR)', 'Norm Accrual Score (W)']},
            {'output_col': 'Beta', 'columns': ['Norm Beta (IQR)', 'Norm Beta (W)']},
            {'output_col': 'Final Model Score', 'columns': ['Final Model Score (IQR)', 'Final Model Score (W)']}
        ]

        z_columns = []

        for factor in factors:
            output_col = factor['output_col']
            col_IQR, col_W = factor['columns']
            # Use IQR score if available, otherwise use W score
            df[output_col] = df.get(col_IQR, np.nan).combine_first(df.get(col_W, np.nan))

            # Calculate Z-scores
            if df[output_col].notna().any():  # Check if any values are present
                z_col = f'z_{output_col.lower().replace(" ", "_")}'  # Create a Z-score column name
                # Invert sign for specified valuation variables
                if output_col in ['Value', 'PEG', 'Dividend Payout Ratio']:
                    df[z_col] = zscore(-df[output_col])
                else:
                    df[z_col] = zscore(df[output_col])
                z_columns.append(z_col)

        # Aggregate Z-score as the mean of individual Z-scores
        df['zaggr'] = df[z_columns].mean(axis=1)
        
        return df

    # Calculate Z-scores and display the results
    data = calculate_z_scores(data)

    # Define and calculate group scores
    groups = {
        'Profitability Group': ['z_roe', 'z_roa', 'z_net_profit_margin'],
        'Growth Group': ['z_5y_growth_gross_profit', 'z_5y_ni_bv_growth', 'z_5y_ni_asset_growth'],
        'Payout Group': ['z_dividend_payout_ratio', 'z_pct_change_shares_outstanding'],
        'Safety Group': ['z_debt_to_equity', 'z_pre_tax_interest_coverage']
    }

    for group_name, group_factors in groups.items():
        data[group_name] = data[group_factors].mean(axis=1)

    data['Total Composite Z-score'] = data[list(groups.keys())].mean(axis=1)
    data['Difference'] = data['Final Model Score'] - data['Total Composite Z-score']

    # Create the final DataFrame
    final_columns = ['Company Name', 'Exchange Name (VND)', 'CUSIP', 'FactSet Econ Sector',
                     'FactSet Ind', 'Gen Sec Type Desc', 'Final Model Score',
                     'Profitability Group', 'Growth Group', 'Payout Group', 'Safety Group',
                     'Total Composite Z-score', 'Difference']
    
    # Check if all columns exist in data
    final_data = data[[col for col in final_columns if col in data.columns]]

    # Display final data
    st.write("Final Data:")
    st.dataframe(final_data)

    # Optional: Save processed data as downloadable file
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(data)
    st.download_button(
        label="Download Processed Data as CSV",
        data=csv,
        file_name='processed_data.csv',
        mime='text/csv'
    )
