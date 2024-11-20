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

    # Initialize the analysed log dataframe
    df_valid_rows = pd.DataFrame()

    # Parse and analyse the MeasureResult files
    for log_file in log_files:

        # Echo a progress counter of current file index / total file amount
        print("Parsing and analysing file {} / {}...".format(log_files.index(log_file) + 1, len(log_files)))
                                                                                                
        # Extract log file name
        log_file_name = os.path.basename(log_file)

        log_data = stp.parse_log_file(log_file) # Parse the log file
        df_log_data = pd.DataFrame.from_dict(log_data).ffill(axis=0) # Convert the log data to a pandas DataFrame and fill NaN values

        # Identify first valid spreader tracking calculation value
        valid_rows = df_log_data[df_log_data['SpTrRes_Event_code'] == 5.0]
        if not valid_rows.empty:
            first_valid_row = valid_rows.iloc[0]
        else:
            first_valid_row = df_log_data.iloc[0]

        # Enter log file name to the beginning of the DataFrame
        first_valid_row = pd.concat([pd.Series([log_file_name], index=['log_file_name']), first_valid_row])
        # Append the first valid row to the analysed log dataframe
        df_valid_rows = pd.concat([df_valid_rows, first_valid_row.to_frame().T], ignore_index=True)

        # Move cursor up to print progress counter on the same line
        print("\033[F", end="")

    # Save the analysed log data to an excel file
    output_file = os.path.join(log_root, "Spreader_tracking_analysis.xlsx")
    df_valid_rows.to_excel(output_file, index=False)
    print("Analysed data saved to {}.".format(output_file))

    # Plot 'SpTrMsg_position_Skew'
    df_valid_rows['SpTrMsg_position_Skew'] = pd.to_numeric(df_valid_rows['SpTrMsg_position_Skew']) # Convert to numeric
    df_valid_rows['Timestamp'] = pd.to_datetime(df_valid_rows['Timestamp']) # Convert to datetime
    df_valid_rows = df_valid_rows.sort_values(by='Timestamp') # Sort by timestamp
    df_valid_rows.plot(x='Timestamp', y='SpTrMsg_position_Skew') # Plot
    plt.show()

    return None

def collect_measure_result_files(log_root):
    measure_result_files = []
    for root, dirs, files in os.walk(log_root):
        for file in files:
            if file.startswith("MeasureResult") and file.lower().endswith(".csv"):
                measure_result_files.append(os.path.join(root, file))
    return measure_result_files

if __name__ == '__main__':
    main()