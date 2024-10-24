import pandas as pd
import numpy as np

# Set pandas option to opt into future behavior regarding downcasting
pd.set_option('future.no_silent_downcasting', True)

# Function to process the uploaded data
def process_multi_factor_model(uploaded_file):
    # Read the file
    data = pd.read_excel(uploaded_file, header=3)

    # Convert 'In Buy List' to numeric
    data['In Buy List'] = pd.to_numeric(data['In Buy List'], errors='coerce')

    # Filter stocks where 'In Buy List' > 0
    data = data[data['In Buy List'] > 0]

    # Pull the best of IQR and W columns
    def pulling_precalculated_data(df):
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
            ('Dividend Payout Ratio_z', 'Payout Score (IQR)', 'Payout Score (W)'),  # Updated name
            ('Pct Change Shares Outstanding_z', 'Chg Shs Outstdg Score (IQR)', 'Chg Shs Outstdg Score (W)'),
            ('Debt-to-Equity_z', 'D/E Score (IQR)', 'D/E Score (W)'),
            ('Pre-tax Interest Coverage_z', 'PreTax Int Cov Score (IQR)', 'PreTax Int Cov Score (W)'),
            ('Accruals_z', 'Norm Accrual Score (IQR)', 'Norm Accrual Score (W)'),
            ('Beta_z', 'Norm Beta (IQR)', 'Norm Beta (W)'),
            ('Final Model Score_z', 'Final Model Score (IQR)', 'Final Model Score (W)')
        ]
        
        for output_col, col_IQR, col_W in factors:
            # Check if either of the columns exists in the DataFrame
            if col_IQR in df.columns or col_W in df.columns:
                # If both columns exist, fill missing values in col_IQR with col_W
                df[output_col] = df[col_IQR].fillna(df[col_W])
            else:
                print(f"Warning: Both {col_IQR} and {col_W} are missing. Skipping {output_col}.")
                df[output_col] = np.nan
        
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

    # Check if 'Modified Final Model 3 Score (IQR)' exists
    if 'Modified Final Model 3 Score (IQR)' in data.columns:
        data['Difference'] = data['Modified Final Model 3 Score (IQR)'] - data['Total Composite Z-score']
    else:
        data['Difference'] = np.nan

    # Create the final DataFrame
    final_columns = ['Company Name', 'Value_z', 'Momentum_z', 'Profitability Group', 'Total Composite Z-score', 'Difference']
    final_data = data[final_columns]

    # Return the final processed data
    return final_data

# Main program to manually input the file name
if __name__ == "__main__":
    # Ask for the Excel file
    uploaded_file = input("Please provide the Excel file name (with .xlsx extension) you want to process: ")

    try:
        # Process the file
        processed_data = process_multi_factor_model(uploaded_file)

        # Ask for output file name
        output_file = input("Please provide the name for the output Excel file (with .xlsx extension): ")
        processed_data.to_excel(output_file, index=False)
        print(f"Processed file saved as {output_file}")

    except FileNotFoundError:
        print("Error: File not found. Please check the file name and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")
