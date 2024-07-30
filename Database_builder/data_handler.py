import pandas as pd
import sqlite3
import os
from dataretrieval import nwis

# Directory paths
csv_file_path = 'data/results/updated_reservoir_attributes.csv'
df = pd.read_csv(csv_file_path)
res_folder_path = 'data/ResOpsUS/time_series_all/'
demands_df = pd.read_csv('data/demands.csv')
diversions_df = pd.read_csv('data/modeled_diversions.csv')

# IDs for dams and USGS gages
dam_name_ids = ['WA00169', 'OR00685', 'CO01656']
USGS_gage_ids = ['09019500', '09040500']
div_ids = ['3600606', '3600642']

# Filter DataFrame based on dam IDs
filtered_df = df[df['NID ID'].isin(dam_name_ids)]
print(filtered_df)

# Connect to SQLite database
conn = sqlite3.connect('optional_db.db')
cursor = conn.cursor()

# Insert POI data into the database
def insert_poi(poiid, poi_type_id, poi_lat, poi_lon, poi_native_id, poi_flow_com_id):
    try:
        cursor.execute('''
            INSERT INTO POI (POIID, POI_TypeID, POI_Lat, POI_Lon, POI_NativeID, POI_Flow_ComID)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (poiid, poi_type_id, poi_lat, poi_lon, poi_native_id, poi_flow_com_id))
        print(f"Inserted POI with POIID {poiid}")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

# Insert POI values into the database
def insert_poi_values(dataval, localtime, poiid, variableid):
    try:
        cursor.execute('''
            INSERT INTO POI_Values (DataValue, LocalDateTime, POIID, VariableID)
            VALUES (?, ?, ?, ?)
        ''', (dataval, localtime, poiid, variableid))
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

# Check if POIID exists in the database
def poiid_exists(poiid):
    cursor.execute('''
        SELECT 1 FROM POI WHERE POIID = ?
    ''', (poiid,))
    return cursor.fetchone() is not None

# Get site coordinates using NWIS
def get_site_coordinates(site_number):
    try:
        site_info = nwis.get_info(sites=site_number)
        latitude = site_info[0]['dec_lat_va'].iloc[0]
        longitude = site_info[0]['dec_long_va'].iloc[0]
        return latitude, longitude
    except (KeyError, IndexError) as e:
        print(f"Error retrieving coordinates for site {site_number}: {e}")
        return None, None

# Process dam data
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
        poi_flow_com_id=12254156  # Example flow com ID, replace as needed
    )

    file_name = f"ResOpsUS_{row['DAM_ID']}.csv"
    file_path = os.path.join(res_folder_path, file_name)

    # Check if the file exists and read it
    if os.path.exists(file_path):
        print(f"File found: {file_path}")
        dam_df = pd.read_csv(file_path)
        variable_names = ['inflow', 'outflow', 'storage']
        var_id_start = 1

        for var_id, var_name in enumerate(variable_names, start=var_id_start):
            if var_name in dam_df.columns:
                for index, dam_row in dam_df.iterrows():
                    insert_poi_values(
                        dataval=dam_row[var_name],
                        localtime=dam_row['date'],
                        poiid=poiid,
                        variableid=var_id,
                    )

# Process USGS gage data
for gage_id in USGS_gage_ids:
    poiid = f"USGS_{gage_id}"

    if poiid_exists(poiid):
        print(f"POIID {poiid} already exists in the database, skipping insertion.")
        continue

    try:

        nwis_data_raw = nwis.get_dv(sites=gage_id, parameterCd='00060', startDT='1880-01-01')

        nwis_data = nwis_data_raw[0]
        print(nwis_data.head())
        latitude, longitude = get_site_coordinates(gage_id)
    except Exception as e:
        print(f"Error retrieving data for gage ID {gage_id}: {e}")
        continue

    if not nwis_data.empty and latitude is not None and longitude is not None:
        insert_poi(
            poiid=poiid,
            poi_type_id=1,
            poi_lat=latitude,
            poi_lon=longitude,
            poi_native_id=gage_id,
            poi_flow_com_id=None
        )

        for index, entry in nwis_data.iterrows():
            insert_poi_values(
                dataval=entry['00060_Mean'],
                localtime=index.isoformat(),
                poiid=poiid,
                variableid=1,
            )
    else:
        print(f"No data found or incomplete data for gage ID: {gage_id}")

diversion_data = diversions_df[diversions_df['WDID'].isin(div_ids)]


for index, row in diversion_data.iterrows():
    poiid = f"DIV_{row['WDID']}"
    latitude = row['Y']
    longitude = row['X']

    if not poiid_exists(poiid):
        insert_poi(
            poiid=poiid,
            poi_type_id=2,
            poi_lat=latitude,
            poi_lon=longitude,
            poi_native_id=row['WDID'],
            poi_flow_com_id=None
        )

for div_id in div_ids:
    if div_id in demands_df.columns:
        for index, row in demands_df.iterrows():


            poiid = f"DIV_{div_id}"

            insert_poi_values(
                dataval=row[div_id],
                localtime=row['Date'],
                poiid=poiid,
                variableid=4,
            )

# Commit changes and close the database connection
conn.commit()
cursor.close()
conn.close()

