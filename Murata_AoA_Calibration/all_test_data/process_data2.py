'''
This python script will process the raw data collected from the Murata AoA calibration tests 
which are stored as csv files in the directory ./anchor_1_Initiator_20260408. 
It will read the raw data files, extract the relevant information, and save it in a structured csv format
with columns for Real Azimuth, Real Elevation, NLOS, Distance, AoA1, AoA2, RSSI, PDoA1, and PDoA2.
The colated data will be saved in the file ALL_anchor_1_Initiator_20260408.csv for further analysis and visualization.

The raw data files are named in the format ranging_Initiator_YYYYMMDD_HHMMSS.csv,
and each file contains multiple rows of data corrseponding for repeated measurements
at the same Real Azimuth and Real Elevation for the given raw data file.
The columns in the raw data files include: Timestamp, Sequence, NLoS, 
Distance_cm, Azimuth_deg, Elevation_deg, Azimuth_FOM, Elevation_FOM, RSSI, PDoA1, and PDoA2.

To find the Real Azimuth and Real Elevation for each raw data file, we will extract that information 
from ./anchor_1_Initiator_20260408/!Timestamp_Map.csv which contains the columns
Azimuth, Elevation, and Timestamp
The data in the Timestamp column is in the format YYYYMMDD_HHMMSS and corresponds to the timestamp in the raw data file names.

The script will iterate through the Timestamp_Map.csv file,and for each timestamp, it will find the corresponding raw data file, read the data, and extract the relevant information to save in the output csv file.
'''

import os
import pandas as pd

def process_data(raw_data_dir, timestamp_map_file, output_file):
    # Read the timestamp map file to get the mapping of timestamps to real azimuth and elevation
    timestamp_map = pd.read_csv(timestamp_map_file)

    # Initialize a list to store the processed data
    processed_data = []

    # Iterate through each row in timestamp map to find the corresponding raw data file and extract information
    for index, row in timestamp_map.iterrows():
        timestamp = row['Timestamp']
        real_azimuth = row['Azimuth']
        real_elevation = row['Elevation']

        # Find the corresponding raw data file
        raw_data_file = os.path.join(raw_data_dir, f"ranging_Initiator_{timestamp}.csv")
        if os.path.exists(raw_data_file):
            # Read the raw data file
            raw_data = pd.read_csv(raw_data_file)

            # Process each row in the raw data file and append to the processed data list
            for index, data_row in raw_data.iterrows():
                processed_data.append({
                    'Real Azimuth': real_azimuth,
                    'Real Elevation': real_elevation,
                    'NLOS': data_row['NLoS'],
                    'Distance': data_row['Distance_cm'],
                    'AoA1': data_row['Azimuth_deg'],
                    'AoA2': data_row['Elevation_deg'],
                    'RSSI': data_row['RSSI'],
                    'PDoA1': data_row['PDoA1'],
                    'PDoA2': data_row['PDoA2']
                })
        else:
            print(f"Warning: No raw data file found for timestamp {timestamp}")

    





    '''
    for filename in os.listdir(raw_data_dir):
        if filename.endswith('.csv') and filename != '!Timestamp_Map.csv':
            # Extract the timestamp from the filename
            timestamp = filename.split('_')[2] + '_' + filename.split('_')[3].split('.')[0]

            # Find the corresponding real azimuth and elevation from the timestamp map
            row = timestamp_map[timestamp_map['Timestamp'] == timestamp]
            if not row.empty:
                real_azimuth = row['Azimuth'].values[0]
                real_elevation = row['Elevation'].values[0]

                # Read the raw data file
                raw_data = pd.read_csv(os.path.join(raw_data_dir, filename))

                # Process each row in the raw data file and append to the processed data list
                for index, data_row in raw_data.iterrows():
                    processed_data.append({
                        'Real Azimuth': real_azimuth,
                        'Real Elevation': real_elevation,
                        'NLOS': data_row['NLoS'],
                        'Distance': data_row['Distance_cm'],
                        'AoA1': data_row['Azimuth_deg'],
                        'AoA2': data_row['Elevation_deg'],
                        'RSSI': data_row['RSSI'],
                        'PDoA1': data_row['PDoA1'],
                        'PDoA2': data_row['PDoA2']
                    })

            else:
                print(f"Warning: No matching timestamp found for file {filename}")
    '''
    # Convert the processed data list to a DataFrame and save as a new CSV file
    processed_df = pd.DataFrame(processed_data)
    processed_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    raw_data_directory = './anchor_0_Initiator_20260409'
    timestamp_map_csv = './anchor_0_Initiator_20260409/!Timestamp Map(RP0).csv'
    output_csv_file = 'ALL_anchor_0_Initiator_20260409.csv'

    process_data(raw_data_directory, timestamp_map_csv, output_csv_file)