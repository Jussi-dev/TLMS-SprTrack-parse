import sys
import matplotlib.pyplot as plt
import pandas as pd
from tkinter import filedialog
import os
# Append path to the parser module
sys.path.append('/C:/Users/henttju/Python scripts/TLMS log analysis/TLMS SprTrack parse')
import SprTrc_parser as stp # Import the parser module


# Analyse spreader tracking data
def main():
    # Ask for the root directory of the log files
    log_root = filedialog.askdirectory()

    # Collect MeasureResult files under log root
    log_files = collect_measure_result_files(log_root)
    print("Found {} MeasureResult files.".format(len(log_files)))

    # define the analysed log dataframe
    df_processed_logs = pd.DataFrame()

    # Parse and analyse the MeasureResult files
    for log_file in log_files:
        # Initialize the analysis data structure
        df_current_analysis = initialize_analysis_data_structure()

        # Echo a progress counter of current file index / total file amount
        print("Parsing and analysing file {} / {}...".format(log_files.index(log_file) + 1, len(log_files)))

        # =================== Data extraction ===================                                                                               
        # Extract log file name and enter it to the current analysis DataFrame
        log_file_name = os.path.basename(log_file) # Extract the log file name
        df_current_analysis.loc[0, 'log_file_name'] = log_file_name # Enter the log file name to the DataFrame
        
        # Parse the log file and convert the log data to a pandas DataFrame
        log_data = stp.parse_log_file(log_file) # Parse the log file
        df_log_data = pd.DataFrame.from_dict(log_data).ffill(axis=0).infer_objects() # Convert the log data to a pandas DataFrame, fill NaN values, and infer objects

        # Extract the timestamp of the log file and enter it to the DataFrame
        df_current_analysis.loc[0, 'log_file_timestamp'] = df_log_data.iloc[0]['Timestamp'] # Extract the timestamp of the log file from the first row

        # Extract job pre info from the log file
        extract_job_info(df_current_analysis, df_log_data)
        # ====================================================

        # =================== Data analysis ===================
        # Find the first valid row of 'SpTrMsg_Skew'
        extract_first_valid_spreader_data(df_current_analysis, df_log_data)
        # ====================================================

        # =================== Data aggregation ===================
        # Append the first valid row to the analysed log dataframe
        df_processed_logs = pd.concat([df_processed_logs, df_current_analysis], ignore_index=True)
        # ====================================================

        # Move cursor up to print progress counter on the same line
        print("\033[F", end="")

    # Save the analysed log data to an excel file
    output_file = os.path.join(log_root, "Spreader_tracking_analysis.xlsx")
    df_processed_logs.to_excel(output_file, index=False)
    print("Analysed data saved to {}.".format(output_file))

    # =================== Plots ===================
    # Plot 'SpTrMsg_position_Skew'
    if False:
        plot_initial_ath_skew(df_processed_logs)
    # =============================================

    return None

def extract_job_info(df_current_analysis, df_log_data):
    df_current_analysis.loc[0, 'Lane'] = df_log_data.iloc[0]['Lane'].astype(int)
    df_current_analysis.loc[0, 'Task'] = df_log_data.iloc[0]['Task']
    df_current_analysis.loc[0, 'Position'] = df_log_data.iloc[0]['Position']
    df_current_analysis.loc[0, 'Chassis_length'] = df_log_data.iloc[0]['Chassis_length']
    df_current_analysis.loc[0, 'Chassis_type'] = df_log_data.iloc[0]['Chassis_type']
    df_current_analysis.loc[0, 'Cont_Length'] = df_log_data.iloc[0]['Cont_Length'].astype(int)
    df_current_analysis.loc[0, 'Cont_Width'] = df_log_data.iloc[0]['Cont_Width'].astype(int)
    df_current_analysis.loc[0, 'Cont_Height'] = df_log_data.iloc[0]['Cont_Height'].astype(int)

# Extract the first valid spreader tracking calculation values
def extract_first_valid_spreader_data(df_current_analysis, df_log_data):
    # 'SpTrMsg_Skew_1st_valid',
    # 'SpTrRes_Skew_1st_valid',
    # 'SpTrRes_Skew_1st_valid_timestamp'

    # Find the first valid row of 'SpTrMsg_Skew' 
    valid_rows = df_log_data[df_log_data['SpTrRes_Event_code'] == 5.0]
    if not valid_rows.empty:
        df_current_analysis.loc[0, 'SpTrRes_Skew_1st_valid_timestamp'] = pd.to_datetime(valid_rows.iloc[0]['Timestamp'], errors='coerce')
        df_current_analysis.loc[0, 'SpTrRes_Skew_1st_valid'] = valid_rows.iloc[0]['SpTrRes_calc_Skew']
        df_current_analysis.loc[0, 'SpTrMsg_Skew_1st_valid'] = valid_rows.iloc[0]['SpTrMsg_position_Skew']
    else:
        df_current_analysis.loc[0, 'SpTrRes_Skew_1st_valid_timestamp'] = None
        df_current_analysis.loc[0, 'SpTrRes_Skew_1st_valid'] = None
        df_current_analysis.loc[0, 'SpTrMsg_Skew_1st_valid'] = None

    return None

# Plot the 'SpTrMsg_position_Skew' and 'SpTrRes_calc_Skew' initial values over time in ATH
def plot_initial_ath_skew(df_processed_logs):
    df_processed_logs['SpTrMsg_Skew_1st_valid'] = pd.to_numeric(df_processed_logs['SpTrMsg_Skew_1st_valid'], errors='coerce') # Convert to numeric
    df_processed_logs = df_processed_logs.sort_values(by='SpTrRes_Skew_1st_valid_timestamp') # Sort by timestamp
    df_processed_logs.plot(x='SpTrRes_Skew_1st_valid_timestamp', y=['SpTrMsg_Skew_1st_valid', 'SpTrRes_Skew_1st_valid'], figsize=(12, 6)) # Plot with increased size
    plt.xticks(rotation=45, ha='right') # Rotate x ticks for better visibility and align them to the right
    plt.tight_layout() # Adjust layout to ensure everything fits
    plt.show()
    return None

# Initialize analysis data structure of the MeasureResult files
def initialize_analysis_data_structure():
    df = pd.DataFrame(columns=[
        'log_file_name',
        'log_file_timestamp',
        'Lane',
        'Task',
        'Position',
        'Chassis_length',
        'Chassis_type',
        'Cont_Length',
        'Cont_Width',
        'Cont_Height',
        'SpTrRes_Skew_1st_valid_timestamp',
        'SpTrRes_Skew_1st_valid',
        'SpTrMsg_Skew_1st_valid'
    ])
    return df

def collect_measure_result_files(log_root):
    measure_result_files = []
    for root, dirs, files in os.walk(log_root):
        for file in files:
            if file.startswith("MeasureResult") and file.lower().endswith(".csv"):
                measure_result_files.append(os.path.join(root, file))
    return measure_result_files

if __name__ == '__main__':
    main()