import os
import re
import tkinter as tk
from tkinter import filedialog
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np
from scipy.signal import detrend
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

class ParsingState(Enum):
    INIT            = 0
    SEARCH_TLMS_MEASUREMENT_VALUES = 1
    SEARCH_TLMS_MEASUREMENT_START = 2
    SEARCH_SPREADER_TRACKING_VALUES = 3

def init_measure_result_data():
    measure_result_data ={
        'Timestamp' : None,
        'Measurement_ID' : None,
        'Lane' : None,
        'Task' : None,
        'Position' : None,
        'Chassis_length' : None,
        'Chassis_type' : None,
        'Cont_Length' : None,
        'Cont_Width' : None,
        'Cont_Height' : None,
        'Lane_Status' : None,
        'Measurement_Status' : None,
        'Assumed_trailer' : None,
        'Point_Center_X' : None,
        'Point_Center_Y' : None,
        'Point_Center_Z' : None,
        'Skew' : None,
        'Tilt' : None,
        'Nr_of_detected_TL' : None,
        'SpTrMsg_length' : None,
        'SpTrMsg_position_X' : None,
        'SpTrMsg_position_Y' : None,
        'SpTrMsg_position_Z' : None,
        'SpTrMsg_position_Skew' : None,
        'SpTrRes_TLMS_Status' : None,
        'SpTrRes_calc_X' : None,
        'SpTrRes_calc_Y' : None,
        'SpTrRes_calc_Skew' : None,
        'SpTrRes_Reliability' : None,
        'SpTrRes_Event_code' : None,
        'SpTrRes_Event_desc' : None
    }
    return measure_result_data

def parse_timestamp(match_timestamp):
    return datetime.strptime(match_timestamp, '%d.%m.%Y %H:%M:%S;%f')

def parse_log_file(log_file):
    parsed_data = []
    
    with open(log_file, 'r') as file:
        log_lines = file.readlines()
    
    # Search and store TLMS trailer/container measurement values

    state = ParsingState.INIT
    for log_line in log_lines:
        data = init_measure_result_data() # Store data and status values
        if state == ParsingState.INIT:
            state = ParsingState.SEARCH_TLMS_MEASUREMENT_START
        if state == ParsingState.SEARCH_TLMS_MEASUREMENT_START:
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - ASCCS Start Measurement Message received')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = key_match.group(1)
                timestamp = parse_timestamp(timestamp)
                # print(f"Timestamp: {timestamp}, ASCCS Start Measurement Message received")
                state = ParsingState.SEARCH_TLMS_MEASUREMENT_VALUES

        elif state == ParsingState.SEARCH_TLMS_MEASUREMENT_VALUES:

            # Search for the TLMS measurement job
            # Measurement_ID
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Measurement ID:\s*(.*?)$')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Measurement_ID'] = str(key_match.group(2)).strip()
                else:
                    data['Timestamp'] = timestamp
                    data['Measurement_ID'] = str(key_match.group(2)).strip()
                    parsed_data.append(data)
                continue            

            # Search for the TLMS measurement job
            # Lane
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Lane:\s*(\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Lane'] = int(key_match.group(2))
                else:
                    data['Timestamp'] = timestamp
                    data['Lane'] = int(key_match.group(2))
                    parsed_data.append(data)
                continue

            # Search for the TLMS measurement job
            # Task
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Task:\s*(\d*\s*-\s*[\w ]*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Task'] = str(key_match.group(2)).strip()
                else:
                    data['Timestamp'] = timestamp
                    data['Task'] = str(key_match.group(2)).strip()
                    parsed_data.append(data)
                continue

            # Search for the TLMS measurement job
            # Position
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Pos:\s*(\d*\s*-\s*[\w ]*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Position'] = str(key_match.group(2)).strip()
                else:
                    data['Timestamp'] = timestamp
                    data['Position'] = str(key_match.group(2)).strip()
                    parsed_data.append(data)
                continue

            # Search for the TLMS measurement job
            # Chassis length
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Len:\s*(.*?)$')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Chassis_length'] = str(key_match.group(2)).strip()
                else:
                    data['Timestamp'] = timestamp
                    data['Chassis_length'] = str(key_match.group(2)).strip()
                    parsed_data.append(data)
                continue

            # Search for the TLMS measurement job
            # Chassis type
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Type:\s*(\d*\s*-\s*[\w ]*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Chassis_type'] = str(key_match.group(2)).strip()
                else:
                    data['Timestamp'] = timestamp
                    data['Chassis_type'] = str(key_match.group(2)).strip()
                    parsed_data.append(data)
                continue

            # Search for the TLMS measurement job
            # Container length, width, height
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Cont\.\s*(Length|Width|Height):\s*(\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                # Check if there is already data with found timestamp
                if check_timestamp(parsed_data, timestamp):
                    # There is already data with this timestamp
                    if key_match.group(2) == "Length":
                        parsed_data[-1]['Cont_Length'] = int(key_match.group(3))
                    elif key_match.group(2) == "Width":
                        parsed_data[-1]['Cont_Width'] = int(key_match.group(3))
                    elif key_match.group(2) == "Height":
                        parsed_data[-1]['Cont_Height'] = int(key_match.group(3))
                else:
                    data['Timestamp'] = timestamp
                    if key_match.group(2) == "Length":
                        data['Cont_Length'] = int(key_match.group(3))
                    elif key_match.group(2) == "Width":
                        data['Cont_Width'] = int(key_match.group(3))
                    elif key_match.group(2) == "Height":
                        data['Cont_Height'] = int(key_match.group(3))
                    parsed_data.append(data)
                continue

            # Search for the TLMS measurement job
            # Lane status
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - LaneStat\s*-\s*(\w*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Lane_Status'] = str(key_match.group(2)).strip()
                else:
                    data['Timestamp'] = timestamp
                    data['Lane_Status'] = str(key_match.group(2)).strip()
                    parsed_data.append(data)
                continue            

            # Search for the TLMS measurement job
            # Measurement status
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; -  \| MeasStat\s*-\s*(\w*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Measurement_Status'] = str(key_match.group(2)).strip()
                else:
                    data['Timestamp'] = timestamp
                    data['Measurement_Status'] = str(key_match.group(2)).strip()
                    parsed_data.append(data)
                continue 

            # Measurement result
            # Assumed_trailer
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Assuming\s*([\w_]*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Assumed_trailer'] = str(key_match.group(2)).strip()
                else:
                    data['Timestamp'] = timestamp
                    data['Assumed_trailer'] = str(key_match.group(2)).strip()
                    parsed_data.append(data)
                continue             

            # Search for the TLMS measurement Job
            # X, Y and Z
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Point Center X\/Y\/Z:\s*(\d*) / (\d*) / (\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Point_Center_X'] = int(key_match.group(2))
                    parsed_data[-1]['Point_Center_Y'] = int(key_match.group(3))
                    parsed_data[-1]['Point_Center_Z'] = int(key_match.group(4))
                else:
                    data['Timestamp'] = parse_timestamp(key_match.group(1))
                    data['Point_Center_X'] = int(key_match.group(2))
                    data['Point_Center_Y'] = int(key_match.group(3))
                    data['Point_Center_Z'] = int(key_match.group(4))
                    parsed_data.append(data)
                continue

            # Search for the TLMS measurement job
            # Skew
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Skew:\s*(-?\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Skew'] = int(key_match.group(2))
                else:
                    data['Timestamp'] = timestamp
                    data['Skew'] = int(key_match.group(2))
                    parsed_data.append(data)
                continue       

            # Search for end of TLMS measurement
            # Tilt
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Tilt\s*(-?\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Tilt'] = int(key_match.group(2))
                else:
                    data['Timestamp'] = timestamp
                    data['Tilt'] = int(key_match.group(2))
                    parsed_data.append(data)
                continue 

            # Search for end of TLMS measurement
            # Number of detected twistlocks
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; -- Number of detected twist locks \(TL\):\s*(\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['Nr_of_detected_TL'] = int(key_match.group(2))
                else:
                    data['Timestamp'] = timestamp
                    data['Nr_of_detected_TL'] = int(key_match.group(2))
                    parsed_data.append(data)
                continue
            
            # Search for end of TLMS measurement
            # Measurement finished OR Spreader Tracking Message received OR Spreader tracking results
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Measurement finished| - Spreader Tracking Message received|Spreader tracking results:')
            key_match = pattern.search(log_line)
            if key_match:
                state = ParsingState.SEARCH_SPREADER_TRACKING_VALUES

        elif state == ParsingState.SEARCH_SPREADER_TRACKING_VALUES:

            # Search for Spreader tracking message values
            # length, position x/y/z/angle
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Spreader (length|position [XYZ]|position Angle):\s*(-?\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                # Check if there is already data with found timestamp
                if check_timestamp(parsed_data, timestamp):
                    # There is already data with this timestamp
                    if key_match.group(2) == "length":
                        parsed_data[-1]['SpTrMsg_length'] = int(key_match.group(3))
                    if key_match.group(2) == "position X":
                        parsed_data[-1]['SpTrMsg_position_X'] = int(key_match.group(3))
                    elif key_match.group(2) == "position Y":
                        parsed_data[-1]['SpTrMsg_position_Y'] = int(key_match.group(3))
                    elif key_match.group(2) == "position Z":
                        parsed_data[-1]['SpTrMsg_position_Z'] = int(key_match.group(3))
                    elif key_match.group(2) == "position Angle":
                        parsed_data[-1]['SpTrMsg_position_Skew'] = int(key_match.group(3))
                else:
                    data['Timestamp'] = timestamp
                    if key_match.group(2) == "length":
                        data['SpTrMsg_length'] = int(key_match.group(3))
                    if key_match.group(2) == "position X":
                        data['SpTrMsg_position_X'] = int(key_match.group(3))
                    elif key_match.group(2) == "position Y":
                        data['SpTrMsg_position_Y'] = int(key_match.group(3))
                    elif key_match.group(2) == "position Z":
                        data['SpTrMsg_position_Z'] = int(key_match.group(3))
                    elif key_match.group(2) == "position Angle":
                        data['SpTrMsg_position_Skew'] = int(key_match.group(3))
                    parsed_data.append(data)
                continue
            
            # Search for Spreader tracking results values
            # TLMS Status
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - TLMS Status:\s*(\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['SpTrRes_TLMS_Status'] = int(key_match.group(2))
                else:
                    data['Timestamp'] = timestamp
                    data['SpTrRes_TLMS_Status'] = int(key_match.group(2))
                    parsed_data.append(data)
                continue

            # position X, position Y, Skew
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Spreader calc\. (position X|position Y|Skew):\s*(-?\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                # Check if there is already data with found timestamp
                if check_timestamp(parsed_data, timestamp):
                    if key_match.group(2) == "position X":
                        parsed_data[-1]['SpTrRes_calc_X'] = int(key_match.group(3))
                    elif key_match.group(2) == "position Y":
                        parsed_data[-1]['SpTrRes_calc_Y'] = int(key_match.group(3))
                    elif key_match.group(2) == "Skew":
                        parsed_data[-1]['SpTrRes_calc_Skew'] = int(key_match.group(3))
                else:
                    data['Timestamp'] = timestamp
                    if key_match.group(2) == "position X":
                        data['SpTrRes_calc_X'] = int(key_match.group(3))
                    elif key_match.group(2) == "position Y":
                        data['SpTrRes_calc_Y'] = int(key_match.group(3))
                    elif key_match.group(2) == "Skew":
                        data['SpTrRes_calc_Skew'] = int(key_match.group(3))
                    parsed_data.append(data)
                continue

            # Calculation reliability
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Calc\. reliability:\s*(\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                # Check if there is already data with found timestamp
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['SpTrRes_Reliability'] = int(key_match.group(2))
                else:
                    data['Timestamp'] = timestamp
                    data['SpTrRes_Reliability'] = int(key_match.group(2))
                    parsed_data.append(data)
                continue

            # Error and event code
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Error/Event code:\s*(\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                # Check if there is already data with found timestamp
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['SpTrRes_Event_code'] = int(key_match.group(2))
                else:
                    data['Timestamp'] = timestamp
                    data['SpTrRes_Event_code'] = int(key_match.group(2))
                    parsed_data.append(data)
                continue

            # Error and event description
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Error/Event description:\s*([a-zA-Z -]+)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                # Check if there is already data with found timestamp
                if check_timestamp(parsed_data, timestamp):
                    parsed_data[-1]['SpTrRes_Event_desc'] = str(key_match.group(2))
                else:
                    data['Timestamp'] = timestamp
                    data['SpTrRes_Event_desc'] = str(key_match.group(2))
                    parsed_data.append(data)
                continue

    if len(parsed_data) < 1:
        parsed_data.append(data)

    return parsed_data

def check_timestamp(parsed_data, timestamp):
    if len(parsed_data) > 0:
        delta = abs(timestamp - parsed_data[-1]['Timestamp'])
        in_window = delta < timedelta(milliseconds=2)
        return in_window
    else:
        return False

def handle_logs(log_files):
    data_logs = []
    for file in log_files:
        # Parse log file
        df_parsed_log_file = pd.DataFrame.from_dict(parse_log_file(file))

        # Generate log file name
        log_file_name = generate_log_filename(file, df_parsed_log_file)
                
        # Fill missing values
        df_parsed_log_file = df_parsed_log_file.ffill(axis=0)
        data_logs.append(df_parsed_log_file) # Parsed data values
        df_parsed_log_file.to_csv("Output/" + log_file_name + ".csv")

        analyze_spreader_movement(df_parsed_log_file, log_file_name)

def generate_log_filename(file, df_parsed_log_file):
    if not pd.isna(df_parsed_log_file.at[0, 'Lane']):
        Lane = str(int(df_parsed_log_file.at[0, 'Lane']))
    else:
        Lane = "xx"

    if not pd.isna(df_parsed_log_file.at[0, 'Position']):
        Pos = str(df_parsed_log_file.at[0, 'Position']).split('-')
        Pos = Pos[1].strip()
    else:
        Pos = "yy"

    if not pd.isna(df_parsed_log_file.at[0, 'Task']):
        Task = str(df_parsed_log_file.at[0, 'Task']).split('-')
        Task = Task[1].strip()
    else:
        Task = "na"
            
    log_file_name = "Lane_" + Lane + "_" + "Pos_" + Pos + "_" + Task + "_" + os.path.splitext(os.path.basename(file))[0]
        
    if df_parsed_log_file.empty:
        print(log_file_name + " is empty")
    else:
        if not (df_parsed_log_file['SpTrMsg_position_Z'] < 5000.0).any():
            log_file_name = log_file_name + "_Not_seated"
            print(log_file_name)
    return log_file_name

def analyze_spreader_movement(spreader_tracking_data, log_file_name):
    # Select relevant columns and create a copy to avoid the warning
    df_SpTr_data = spreader_tracking_data[['Timestamp', 'Task', 'Measurement_Status', 'Cont_Height', 'Point_Center_Y', 'Point_Center_Z', 'Skew', 'SpTrRes_calc_Y', 'SpTrRes_calc_Skew']].copy()

    # Find Point_Center_Z
    # First data row with TLMS result
    df_first_TLMS_result = df_SpTr_data[df_SpTr_data.Measurement_Status == 'Done']
    if df_first_TLMS_result.empty:
        return
    else:
        df_first_TLMS_result = df_first_TLMS_result.iloc[0]
        print(df_first_TLMS_result['Point_Center_Z'])
        container_height = df_first_TLMS_result['Cont_Height']
        if df_SpTr_data.iloc[0].Task == '1 -  Pick':
            offset = 400.0
        elif df_SpTr_data.iloc[0].Task == '2 -  Place':
            offset = container_height + 360.0
        else:
            offset = 0.0
    
    # Set up gate for signal
    z_limit = df_first_TLMS_result['Point_Center_Z'] + offset
    z_upper_window = 20.0
    z_lower_window = -350.0
    z_upper_limit = z_limit + z_upper_window
    z_lower_limit = z_limit + z_lower_window

    print(f"Upper limit: {z_upper_limit} mm")
    print(f"Lower limit: {z_lower_limit} mm")

    # Filter the data using the gating window and create a copy to avoid the warning
    df_SpTr_data = spreader_tracking_data[
        (spreader_tracking_data['SpTrMsg_position_Z'] >= z_lower_limit) & 
        (spreader_tracking_data['SpTrMsg_position_Z'] <= z_upper_limit)
    ].copy()

    # If the filtered data is empty, return an error message and stop further processing
    if df_SpTr_data.empty:
        print("Filtered data is empty. Please check your filter conditions.")
        return

    # Convert 'Timestamp' to datetime format
    df_SpTr_data['Timestamp'] = pd.to_datetime(df_SpTr_data['Timestamp'])

    # Ensure the data is sorted and set the timestamp as index
    df_SpTr_data = df_SpTr_data.sort_values('Timestamp')
    df_SpTr_data.set_index('Timestamp', inplace=True)

    # Detrend the y_deflection data
    df_SpTr_data['detrended'] = detrend(df_SpTr_data['SpTrRes_calc_Y'])

    # Calculate sampling interval (T) and number of samples (N)
    T = (df_SpTr_data.index[1] - df_SpTr_data.index[0]).total_seconds()
    N = len(df_SpTr_data)

    # Apply FFT to detrended data
    fft_vals = np.fft.fft(df_SpTr_data['detrended'])
    fft_freqs = np.fft.fftfreq(N, T)

    # Find the dominant frequency
    idx = np.argmax(np.abs(fft_vals))
    dominant_freq = np.abs(fft_freqs[idx])
    print(f"Dominant Frequency: {dominant_freq} Hz")

    # Estimate amplitude (peak-to-peak method)
    amplitude = (df_SpTr_data['detrended'].max() - df_SpTr_data['detrended'].min()) / 2
    print(f"Estimated Amplitude: {amplitude}")

    # Create two subplots: one for original data and one for detrended data
    plt.figure(figsize=(12, 10)).suptitle(log_file_name)  # Adjust the figure size as needed

    # First subplot: Original Data
    plt.subplot(2, 1, 1)  # (rows, columns, plot_index)
    plt.plot(df_SpTr_data.index, df_SpTr_data['SpTrRes_calc_Y'], color='blue')

    # Plot trailer Y
    plt.plot(df_SpTr_data.index, df_SpTr_data['Point_Center_Y'], color='red', linestyle='--')
    ax_1 = plt.gca()

    # Force plain formatting without scientific notation
    ax_1.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax_1.ticklabel_format(style='plain', axis='y')
    
    plt.title('Spreader Movement Y')
    plt.xlabel('Timestamp')
    plt.ylabel('SpTrRes_calc_Y (Deflection)')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

    # Second subplot: Skew
    plt.subplot(2, 1, 2)
    plt.plot(df_SpTr_data.index, df_SpTr_data['SpTrRes_calc_Skew'], color='blue')

    # Plot trailer Skew
    plt.plot(df_SpTr_data.index, df_SpTr_data['Skew'], color='red', linestyle='--')

    plt.title('Spreader Movement Skew')
    plt.xlabel('Timestamp')
    plt.ylabel('SpTrRes_calc_Skew')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

    # Adjust layout and show the plots
    plt.tight_layout()
    plt.show()

    # You can continue with other processing steps (FFT, curve fitting, etc.)
def main():
    # Select log files
    log_names = filedialog.askopenfilenames()
    # Parse values
    handle_logs(log_names)


if __name__ == "__main__":
    main()

