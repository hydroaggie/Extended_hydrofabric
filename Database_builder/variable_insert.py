import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('optional_db.db')
cursor = conn.cursor()

# Function to insert data into POI_Type table
def insert_poi_type(poi_type_name, poi_type_source):
    try:
        cursor.execute('''
            SELECT POI_TypeID FROM POI_Type WHERE POI_TypeName = ? AND POI_TypeSource = ?
        ''', (poi_type_name, poi_type_source))
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO POI_Type (POI_TypeName, POI_TypeSource)
                VALUES (?, ?)
            ''', (poi_type_name, poi_type_source))
            print(f"Inserted {poi_type_name} into POI_Type")
        else:
            print(f"{poi_type_name} already exists in POI_Type")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def insert_variable(variable_name, unit):
    try:
        cursor.execute('''
            SELECT VariableID FROM Variables WHERE VariableName = ? AND Unit = ?
        ''', (variable_name, unit))
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO Variables (VariableName, Unit)
                VALUES (?, ?)
            ''', (variable_name, unit))
            print(f"Inserted {variable_name} into Variables")
        else:
            print(f"{variable_name} already exists in Variables")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

poi_types = [
    ('USGS_Gage', 'USGS'),
    ('POD', 'WaDE'),
    ('Reservoir', 'ResOpsUS')
]

for poi_type in poi_types:
    insert_poi_type(poi_type[0], poi_type[1])

variables = [
    ('Inflow', 'CMS'),
    ('Outflow', 'CMS'),
    ('Storage', 'MCM'),
    ('Demand', 'CM')
]

for variable in variables:
    insert_variable(variable[0], variable[1])

conn.commit()
conn.close()