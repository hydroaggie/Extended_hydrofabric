import pandas as pd
import sqlite3
import os

csv_file_path = 'data/results/updated_reservoir_attributes.csv'
df = pd.read_csv(csv_file_path)

res_folder_path = 'data/ResOpsUS/time_series_all/'

name_ids = ['WA00169', 'OR00685', 'CO01656']

filtered_df = df[df['NID ID'].isin(name_ids)]

print(filtered_df)

conn = sqlite3.connect('optional_db.db')
cursor = conn.cursor()

def insert_poi(poiid, poi_type_id, poi_lat, poi_lon, poi_native_id, poi_flow_com_id):
    try:
        cursor.execute('''
            INSERT INTO POI (POIID, POI_TypeID, POI_Lat, POI_Lon, POI_NativeID, POI_Flow_ComID)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (poiid, poi_type_id, poi_lat, poi_lon, poi_native_id, poi_flow_com_id))
        print(f"Inserted POI with POIID {poiid}")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def poiid_exists(poiid):
    cursor.execute('''
        SELECT 1 FROM POI WHERE POIID = ?
    ''', (poiid,))
    return cursor.fetchone() is not None

for index, row in filtered_df.iterrows():
    poiid = f"{row['DAM_ID']}_{row['NID ID']}"

    if poiid_exists(poiid):
        print(f"POIID {poiid} already exists in the database, skipping insertion.")
        continue

    insert_poi(
        poiid=poiid,
        poi_type_id=3,
        poi_lat=row['LAT'],
        poi_lon=row['LONG'],
        poi_native_id=row['NID ID'],
        poi_flow_com_id=12254156
    )
    file_name = f"ResOpsUS_{row['DAM_ID']}.csv"
    file_path = os.path.join(res_folder_path, file_name)

    # Check if the file exists
    if os.path.exists(file_path):
        print(f"File found: {file_path}")
        # Read the CSV file and perform desired operations
        dam_df = pd.read_csv(file_path)

conn.commit()
conn.close()