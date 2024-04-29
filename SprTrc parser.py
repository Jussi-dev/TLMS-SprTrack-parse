import os
import re
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from enum import Enum
import pandas as pd

class ParsingState(Enum):
    INIT            = 0
    SEARCH_TLMS_MEASUREMENT_VALUES = 1
    SEARCH_TLMS_MEASUREMENT_START = 2
    SEARCH_SPREADER_TRACKING_VALUES = 3

def init_measure_result_data():
    measure_result_data ={
        'Timestamp' : None,
        'Point_Center_X' : None,
        'Point_Center_Y' : None,
        'Point_Center_Z' : None,
        'Skew' : None,
        'Tilt' : None,
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
                print(f"Timestamp: {timestamp}, ASCCS Start Measurement Message received")
                state = ParsingState.SEARCH_TLMS_MEASUREMENT_VALUES

        elif state == ParsingState.SEARCH_TLMS_MEASUREMENT_VALUES:
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Point Center X\/Y\/Z:\s*(\d*) / (\d*) / (\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                data['Timestamp'] = parse_timestamp(key_match.group(1))
                data['Point_Center_X'] = int(key_match.group(2))
                data['Point_Center_Y'] = int(key_match.group(3))
                data['Point_Center_Z'] = int(key_match.group(4))
        
                parsed_data.append(data)
                state = ParsingState.SEARCH_SPREADER_TRACKING_VALUES

        elif state == ParsingState.SEARCH_SPREADER_TRACKING_VALUES:
            # Search for Spreader tracking message values
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Spreader position ([XYZ]|Angle):\s*(\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                # Check if there is already data with found timestamp
                if parsed_data[-1]['Timestamp'] == timestamp:
                    # There is already data with this timestamp
                    if key_match.group(2) == "X":
                        parsed_data[-1]['SpTrMsg_position_X'] = int(key_match.group(3))
                    elif key_match.group(2) == "Y":
                        parsed_data[-1]['SpTrMsg_position_Y'] = int(key_match.group(3))
                    elif key_match.group(2) == "Z":
                        parsed_data[-1]['SpTrMsg_position_Z'] = int(key_match.group(3))
                    elif key_match.group(2) == "Angle":
                        parsed_data[-1]['SpTrMsg_position_Skew'] = int(key_match.group(3))
                else:
                    data['Timestamp'] = timestamp
                    if key_match.group(2) == "X":
                        data['SpTrMsg_position_X'] = int(key_match.group(3))
                    elif key_match.group(2) == "Y":
                        data['SpTrMsg_position_Y'] = int(key_match.group(3))
                    elif key_match.group(2) == "Z":
                        data['SpTrMsg_position_Z'] = int(key_match.group(3))
                    elif key_match.group(2) == "Angle":
                        data['SpTrMsg_position_Skew'] = int(key_match.group(3))
                    parsed_data.append(data)
                continue
            
            # Search for Spreader tracking results values
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - Spreader calc\. (position X|position Y|Skew):\s*(\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                # Check if there is already data with found timestamp
                if parsed_data[-1]['Timestamp'] == timestamp:
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

            # TLMS Status
            pattern = re.compile(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2};\d+);\d+; ; ;S; - TLMS Status:\s*(\d*)')
            key_match = pattern.search(log_line)
            if key_match:
                timestamp = parse_timestamp(key_match.group(1))
                if parsed_data[-1]['Timestamp'] == timestamp:
                    parsed_data[-1]['SpTrRes_TLMS_Status'] = key_match.group(2)
                else:
                    data['Timestamp'] = timestamp
                    data['SpTrRes_TLMS_Status'] = key_match.group(2)
                    parsed_data.append(data)
                continue

    return parsed_data

def handle_logs(log_files):
    data_logs = []
    for file in log_files:
        df_parsed_log_file = pd.DataFrame.from_dict(parse_log_file(file))
        data_logs.append(df_parsed_log_file) # Parsed data values
        df_parsed_log_file.to_csv("Parsed.csv")
    
    return data_logs

def main():
    # Select log files
    log_names = filedialog.askopenfilenames()
    # Parse values
    handle_logs(log_names)


if __name__ == "__main__":
    main()

