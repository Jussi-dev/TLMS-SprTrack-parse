import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os

# Append path to the parser module
sys.path.append('/C:/Users/henttju/Python scripts/TLMS log analysis/TLMS SprTrack parse')
import SprTrc_parser as stp # Import the parser module


# Analyse spreader tracking data
def main():
    # Ask for the root directory of the log files
    # Ask if the user wants to define log files from an excel file

    if prompt_use_excel():
        excel_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if excel_file:
            df_excel = pd.read_excel(excel_file)
            log_files = df_excel['filename'].tolist()
            log_root = os.path.dirname(excel_file)
        else:
            print("No excel file selected. Exiting.")
            return
    else:
        log_root = filedialog.askdirectory()
        if not log_root:
            print("No directory selected. Exiting.")
            return

        # Collect MeasureResult files under log root
        log_files = collect_measure_result_files(log_root)
    print("Found {} MeasureResult files.".format(len(log_files)))

    # define the analysed log dataframe
    df_processed_logs = pd.DataFrame()

    # Parse and analyse the MeasureResult files

    print("\n") # Print a newline for better readability
    for log_file in log_files:
        # Initialize the analysis data structure
        df_current_analysis = initialize_analysis_data_structure()

        # Echo a progress counter of current file index / total file amount
        print("\033[F", end="") # Move cursor up one line
        print("Parsing and analysing file {} / {}...".format(log_files.index(log_file) + 1, len(log_files))) # Print the progress counter

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
        if False:
            extract_first_valid_spreader_data(df_current_analysis, df_log_data)

        # Detremine the settling time before final landing
        df_settling_height_range, settling_time = calculate_settling_range(df_log_data, use_slope=False) # Calculate the settling time before final landing
        df_current_analysis.loc[0, 'SpTr_settling_time'] = settling_time # Enter the settling time to the DataFrame

        # Plot the spreader x, y and skew position over time at the settling height range
        plot_settling_height_data(df_log_data, df_settling_height_range)

        # ====================================================

        # =================== Data aggregation ===================
        # Append the first valid row to the analysed log dataframe
        df_processed_logs = pd.concat([df_processed_logs, df_current_analysis], ignore_index=True)
        # ====================================================

        # Move cursor up to print progress counter on the same line

    # Save the analysed log data to an excel file
    output_file = os.path.join(os.getcwd(), "Spreader_tracking_analysis.xlsx")
    df_processed_logs.to_excel(output_file, index=False)
    print("Analysed data saved to {}.".format(output_file))

    # =================== Plots ===================
    # Plot 'SpTrMsg_position_Skew'
    if False:
        plot_initial_ath_skew(df_processed_logs)
    # =============================================

    return None

def plot_settling_height_data(df_log_data, df_settling_height_range):
    fig, axs = plt.subplots(3, 2, figsize=(18, 12)) # Create a figure with 3 rows and 2 columns of subplots
    # Plot spreader x position over time
    df_log_data[(df_log_data['SpTrMsg_position_Z'] < 5500) & (df_log_data['SpTrMsg_position_Z'] > 4000)].plot(x='Timestamp', y=['Point_Center_X', 'SpTrRes_calc_X'], ax=axs[0, 0], title='Spreader X Position Over Time', color='blue')

    # Plot spreader y position over time
    df_log_data[(df_log_data['SpTrMsg_position_Z'] < 5500) & (df_log_data['SpTrMsg_position_Z'] > 4000)].plot(x='Timestamp', y=['Point_Center_Y', 'SpTrRes_calc_Y'], ax=axs[1, 0], title='Spreader Y Position Over Time', color='blue')

    # Plot spreader skew position over time
    df_log_data[(df_log_data['SpTrMsg_position_Z'] < 5500) & (df_log_data['SpTrMsg_position_Z'] > 4000)].plot(x='Timestamp', y=['Skew', 'SpTrRes_calc_Skew'], ax=axs[2, 0], title='Spreader Skew Position Over Time', color='blue')

    # Plot spreader Z position over time
    df_z_range = filter_spreader_data_by_z(df_log_data)
    if not df_z_range.empty:
        df_z_range.plot(x='Timestamp', y='SpTrMsg_position_Z', ax=axs[0, 1], title='Spreader Z Position Over Time')
    else:
        print("No spreader data found in the Z range.\n")

    if df_settling_height_range is not None:
        # Plot spreader x position over time at the settling height range
        df_settling_height_range.plot(x='Timestamp', y=['Point_Center_X', 'SpTrRes_calc_X'], ax=axs[0, 0], title='Spreader tracking X @ settling height', color='red')

        # Plot spreader y position over time at the settling height range
        df_settling_height_range.plot(x='Timestamp', y=['Point_Center_Y', 'SpTrRes_calc_Y'], ax=axs[1, 0], title='Spreader tracking Y @ settling height', color='red')

        # Plot spreader skew position over time at the settling height range
        df_settling_height_range.plot(x='Timestamp', y=['Skew', 'SpTrRes_calc_Skew'], ax=axs[2, 0], title='Spreader tracking skew @ settling height', color='red')

        # Plot spreader Z position over time at the settling height range
        df_settling_height_range.plot(x='Timestamp', y='SpTrMsg_position_Z', ax=axs[0, 1], title='Spreader Z Position @ settling height', color='red')

    else:
        print("No settling height range found.\n")

    # Set common labels for the x and y axes for plot 1
    axs[0, 0].set_xlabel('Timestamp')
    axs[0, 0].set_ylabel('X Position')
    axs[0, 0].yaxis.set_major_formatter(ScalarFormatter(useOffset=False)) # Disable scientific notation
    axs[0, 0].ticklabel_format(useOffset=False, axis='y', style='plain')

    # Set common labels for the x and y axes for plot 2
    axs[1, 0].set_xlabel('Timestamp')
    axs[1, 0].set_ylabel('Y Position')
    axs[1, 0].yaxis.set_major_formatter(ScalarFormatter(useOffset=False)) # Disable scientific notation
    axs[1, 0].ticklabel_format(useOffset=False, axis='y', style='plain')

    # Set common labels for the x and y axes for plot 3
    axs[2, 0].set_xlabel('Timestamp')
    axs[2, 0].set_ylabel('Skew Position')
    axs[2, 0].yaxis.set_major_formatter(ScalarFormatter(useOffset=False)) # Disable scientific notation
    axs[2, 0].ticklabel_format(useOffset=False, axis='y', style='plain')

    # Set common labels for the x and y axes for plot 4
    axs[0, 1].set_xlabel('Timestamp')
    axs[0, 1].set_ylabel('Z Position')
    axs[0, 1].yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    axs[0, 1].ticklabel_format(useOffset=False, axis='y', style='plain')


    # Figure title based on the task, lane, and position
    task, lane, position = extract_task_lane_position(df_settling_height_range)
    fig.suptitle(f"Task: {task}, Lane: {lane}, Position: {position}")

    plt.tight_layout()
    plt.show()

def filter_spreader_data_by_z(df_log_data):
    return df_log_data[(df_log_data['SpTrMsg_position_Z'] < 5500) & (df_log_data['SpTrMsg_position_Z'] > 4000)]


def calculate_settling_range(df_log_data, use_slope=False):
    # Settling time is defined as the time spreader is at the settling height before final landing

    # FInd the target Z height based on the task
    df_measurement_done = df_log_data[df_log_data['Measurement_Status'] == 'Done'] # Find rows with measurement status 'Done'
    if not df_measurement_done.empty:
        # df_measurement_done = df_measurement_done.iloc[0] # Select the first row
        target_z_height = df_measurement_done.iloc[0]['Point_Center_Z'] # Extract the target Z height
    else:
        target_z_height = None

    # Define the settling height based on the task
    if target_z_height is not None:
        if df_measurement_done.iloc[0]['Task'] == '1 -  Pick':
            # Estimate the settling time before final landing
            settling_height = target_z_height + 370 # Z target height + 400 mm offset
        elif df_measurement_done.iloc[0]['Task'] == '2 -  Place':
            # Estimate the settling time before final landing
            settling_height = target_z_height + df_measurement_done.iloc[0]['Cont_Height'] + 360 # Z target height + container height + 360 mm offset
        else:
            settling_height = None
    else:
        settling_height = None

    # Set settling height upper and lower limits
    if settling_height is not None:
        settling_height_upper_limit = settling_height + 50
        settling_height_lower_limit = settling_height - 60
    else:
        settling_height_upper_limit = None
        settling_height_lower_limit = None

    # Find the first row where the spreader is at the settling height before final landing
    if settling_height_upper_limit is not None and settling_height_lower_limit is not None:
        df_settling_height_range = df_log_data[(df_log_data['SpTrMsg_position_Z'] >= settling_height_lower_limit) & (df_log_data['SpTrMsg_position_Z'] <= settling_height_upper_limit)]
        if not df_settling_height_range.empty:
            settling_time = calculate_settling_time(df_settling_height_range)

            # Define a validation spreader height range
            # Spreader z height < 6500 mm
            df_spreader_validation_height_range = df_log_data[df_log_data['SpTrMsg_position_Z'] < 5800]

            # Plot the spreader Z position over time at the settling height range
            # render_settling_height_plot(df_settling_height_range, df_spreader_validation_height_range)
        else:
            settling_time = None
            df_settling_height_range = None
    else:
        settling_time = None
        df_settling_height_range = None

    if use_slope:
        # Settling height is defined as the height in which the spreader height slope is (near) zero
        # Find the first row where the spreader height slope is (near) zero for a certain time period

       # Create the Z_diff column
        df_settling_height_range_filtered = df_settling_height_range.copy()
        df_settling_height_range_filtered['Z_diff'] = df_settling_height_range_filtered['SpTrMsg_position_Z'].diff().fillna(0)

        # Apply a low pass filter to the Z_diff column
        df_settling_height_range_filtered.loc[:, 'Z_diff_filtered'] = df_settling_height_range_filtered['Z_diff'].rolling(window=12, min_periods=1).mean()
        
        # Filter the DataFrame based on the Z_diff_filtered column
        df_settling_height_range = df_settling_height_range_filtered[df_settling_height_range_filtered['Z_diff_filtered'].abs() < 0.5]
        
        if not df_settling_height_range.empty:
            settling_time = calculate_settling_time(df_settling_height_range)
        else:
            settling_time = None
            df_settling_height_range = None

    # df_current_analysis.loc[0, 'SpTr_settling_time'] = settling_time
    return df_settling_height_range, settling_time

def calculate_settling_time(df_settling_height_range):
    settling_time_start = pd.to_datetime(df_settling_height_range.iloc[0]['Timestamp'], errors='coerce')
    settling_time_end = pd.to_datetime(df_settling_height_range.iloc[-1]['Timestamp'], errors='coerce')
    settling_time = settling_time_end - settling_time_start
    return settling_time

def render_settling_height_plot(df_settling_height_range, df_spreader_validation_height_range):
    df_spreader_validation_height_range.plot(x='Timestamp', y='SpTrMsg_position_Z', figsize=(12, 6), label='Validation Height Range')
    df_settling_height_range.plot(x='Timestamp', y='SpTrMsg_position_Z', label='Settling Height Range', ax=plt.gca())
    
    # Plot title based on the task, lane, and position
    task, lane, position = extract_task_lane_position(df_settling_height_range)
    plot_title = f"Task: {task}, Lane: {lane}, Position: {position}" # Plot title
    plt.title(f"{plot_title}")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def extract_task_lane_position(df_settling_height_range):
    if df_settling_height_range is None:
        task, lane, position = None, None, None
    else:
        task = df_settling_height_range.iloc[0]['Task'].split('-')[-1].strip()
        lane = df_settling_height_range.iloc[0]['Lane'].astype(int)
        position = df_settling_height_range.iloc[0]['Position'].split('-')[-1].strip()
    return task,lane,position

def extract_job_info(df_current_analysis, df_log_data):
    df_current_analysis.loc[0, 'Lane'] = df_log_data.iloc[0]['Lane'] if pd.notnull(df_log_data.iloc[0]['Lane']) else None
    df_current_analysis.loc[0, 'Task'] = df_log_data.iloc[0]['Task'] if pd.notnull(df_log_data.iloc[0]['Task']) else None
    df_current_analysis.loc[0, 'Position'] = df_log_data.iloc[0]['Position'] if pd.notnull(df_log_data.iloc[0]['Position']) else None
    df_current_analysis.loc[0, 'Chassis_length'] = df_log_data.iloc[0]['Chassis_length'] if pd.notnull(df_log_data.iloc[0]['Chassis_length']) else None
    df_current_analysis.loc[0, 'Chassis_type'] = df_log_data.iloc[0]['Chassis_type'] if pd.notnull(df_log_data.iloc[0]['Chassis_type']) else None
    df_current_analysis.loc[0, 'Cont_Length'] = df_log_data.iloc[0]['Cont_Length'].astype(int) if pd.notnull(df_log_data.iloc[0]['Cont_Length']) else None
    df_current_analysis.loc[0, 'Cont_Width'] = df_log_data.iloc[0]['Cont_Width'].astype(int) if pd.notnull(df_log_data.iloc[0]['Cont_Width']) else None
    df_current_analysis.loc[0, 'Cont_Height'] = df_log_data.iloc[0]['Cont_Height'].astype(int) if pd.notnull(df_log_data.iloc[0]['Cont_Height']) else None

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
        'SpTrMsg_Skew_1st_valid',
        'SpTr_settling_time'
    ])
    return df

def collect_measure_result_files(log_root):
    measure_result_files = []
    for root, dirs, files in os.walk(log_root):
        for file in files:
            if file.startswith("MeasureResult") and file.lower().endswith(".csv"):
                measure_result_files.append(os.path.join(root, file))
    return measure_result_files

def prompt_use_excel():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    use_excel = messagebox.askyesno("Use Excel file", "Do you want to define log files from an Excel file?")
    return use_excel   

if __name__ == '__main__':
    main()