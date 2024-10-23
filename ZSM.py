import streamlit as st
import pandas as pd 
import numpy as np
from io import BytesIO

st.title('Multi-factor Model Data Processor')

# File uploader
uploaded_file = st.file_uploader("Please upload your Excel file:", type="xlsx")

if uploaded_file is not None:
    # Read the file
    data = pd.read_excel(uploaded_file, header=3)
    st.write("File uploaded successfully.")

   # Convert 'In Buy List' to numeric
    data['In Buy List'] = pd.to_numeric(data['In Buy List'], errors='coerce')

    # Handle NaN values if any (choose one option)
    # Option 1: Drop rows where 'In Buy List' is NaN
    data = data.dropna(subset=['In Buy List'])
    # Option 2: Fill NaN values with 0
    # data['In Buy List'] = data['In Buy List'].fillna(0)

    # Filter stocks where 'In Buy List' > 0
    data = data[data['In Buy List'] > 0]


    # Print columns to verify correct loading
    st.write("Columns available in the DataFrame:")
    st.write(data.columns.tolist())

   # Pull the best of IQR and W columns
    def pulling_precalculated_data(df):
        # Define a list of tuples containing the output column and its corresponding input columns
        factors = [
            ('Value_z', 'Value Score (IQR)', 'Value Score (W)'),
            ('Momentum_z', 'Momentum Score (IQR)', 'Momentum Score (W)'),
            ('PEG_z', 'PEG Score (IQR)', 'PEG Score (W)'),
            ('Earnings Surprise_z', 'Earnings Surprise Score (IQR)', 'Earnings Surprise Score (W)'),
            ('ROE_z', 'Ret on Avg Total Equity (IQR)', 'Ret on Avg Total Equity (W)'),
            ('ROA_z', 'Ret on Avg Total Assets (IQR)', 'Ret on Avg Total Assets (W)'),
            ('Net Profit Margin_z', 'Net Income Margin (IQR)', 'Net Income Margin (W)'),
            ('5Y Growth Gross Profit_z', 'Chg in GP/Sales Score (IQR)', 'Chg in GP/Sales Score (W)'),
            ('5Y NI-BV Growth_z', 'Chg in NI/BV Score (IQR)', 'Chg in NI/BV Score (W)'),
            ('5Y NI-Asset Growth_z', 'Chg in NI/Assets Score (IQR)', 'Chg in NI/Assets Score (W)'),
            ('Dividend Payout Ratio_z', 'Div Pd Score (IQR)', 'Div Pd Score (W)'),
            ('Pct Change Shares Outstanding_z', 'Chg Shs Outstdg Score (IQR)', 'Chg Shs Outstdg Score (W)'),
            ('Debt-to-Equity_z', 'D/E Score (IQR)', 'D/E Score (W)'),
            ('Pre-tax Interest Coverage_z', 'PreTax Int Cov Score (IQR)', 'PreTax Int Cov Score (W)'),
            ('Accruals_z', 'Norm Accrual Score (IQR)', 'Norm Accrual Score (W)'),
            ('Beta_z', 'Norm Beta (IQR)', 'Norm Beta (W)'),
            ('Final Model Score_z', 'Final Model Score (IQR)', 'Final Model Score (W)')
        ]
    
        for output_col, col_IQR, col_W in factors:
            if col_IQR in df.columns and col_W in df.columns:
                df[output_col] = np.where(df[col_IQR].notna(), df[col_IQR], df[col_W])
            elif col_IQR in df.columns:
                df[output_col] = df[col_IQR]
            elif col_W in df.columns:
                df[output_col] = df[col_W]
            else:
                df[output_col] = np.nan  # Assign NaN if neither column exists
    
        return df

    # Pull the best Z-scores from the available columns
    data = pulling_precalculated_data(data)

    # Define and calculate group scores
    groups = {
        'Profitability Group': ['ROE_z', 'ROA_z', 'Net Profit Margin_z'],
        'Growth Group': ['5Y Growth Gross Profit_z', '5Y NI-BV Growth_z', '5Y NI-Asset Growth_z'],
        'Payout Group': ['Dividend Payout Ratio_z', 'Pct Change Shares Outstanding_z'],
        'Safety Group': ['Debt-to-Equity_z', 'Pre-tax Interest Coverage_z']
    }

    for group_name, group_factors in groups.items():
        data[group_name] = data[group_factors].mean(axis=1)

    data['Total Composite Z-score'] = data[list(groups.keys())].mean(axis=1)
    data['Difference'] = data['Modified Final Model 3 Score (IQR)'] - data['Total Composite Z-score']

    # Create the final DataFrame
    final_columns = ['Company Name', 'Exchange Name (VND)', 'CUSIP',
                     'FactSet Econ Sector', 'FactSet Ind', 'Gen Sec Type Desc',
                     'Overall Model Score', 'Profitability Group', 'Growth Group',
                     'Payout Group', 'Safety Group', 'Total Composite Z-score', 'Difference']
    final_data = data[final_columns]

    # Display final data
    st.write("Final Data:")
    st.dataframe(final_data)

    # Save to XLSX in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_data.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.save()
        processed_data = output.getvalue()

    # Provide download button
    st.download_button(
        label="Download Output Excel File",
        data=processed_data,
        file_name='multi_factor_model_output.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    st.success("Data processing complete. You can download the output file above.")
