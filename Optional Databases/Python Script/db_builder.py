import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('optional_db.db')
cursor = conn.cursor()

# Create table for POI_Type
cursor.execute('''
CREATE TABLE IF NOT EXISTS POI_Type (
    POI_TypeID INTEGER PRIMARY KEY,
    POI_TypeName TEXT,
    POI_TypeSource TEXT
)
''')

# Create table for POI
cursor.execute('''
CREATE TABLE IF NOT EXISTS POI (
    POIID INTEGER PRIMARY KEY,
    POI_TypeID INTEGER,
    POI_Lat REAL,
    POI_Lon REAL,
    POI_NativeID INTEGER,
    POI_Flow_ComID INTEGER,
    FOREIGN KEY (POI_TypeID) REFERENCES POI_Type (POI_TypeID)
)
''')

# Create table for Variables
cursor.execute('''
CREATE TABLE IF NOT EXISTS Variables (
    VariableID INTEGER PRIMARY KEY,
    VariableName TEXT,
    Unit TEXT
)
''')

# Create table for Values
cursor.execute('''
CREATE TABLE IF NOT EXISTS POI_Values (
    ValueID INTEGER PRIMARY KEY,
    DataValue REAL,
    LocalDateTime TEXT,
    POIID INTEGER,
    VariableID INTEGER,
    FOREIGN KEY (POIID) REFERENCES POI (POIID),
    FOREIGN KEY (VariableID) REFERENCES Variables (VariableID)
)
''')

# Create table for ET_Precip
cursor.execute('''
CREATE TABLE IF NOT EXISTS ET_Precip (
    ET_PrecipID INTEGER PRIMARY KEY,
    ETDataValue REAL,
    PrecipValue REAL,
    LocalDateTime TEXT,
    POIID INTEGER,
    VariableID INTEGER,
    FOREIGN KEY (POIID) REFERENCES POI (POIID),
    FOREIGN KEY (VariableID) REFERENCES Variables (VariableID)
)
''')

# Create table for Curve_Rules
cursor.execute('''
CREATE TABLE IF NOT EXISTS Curve_Rules (
    Curve_RulesID INTEGER PRIMARY KEY,
    Min_ReleaseValue REAL,
    Target_StorageValue REAL,
    LocalDateTime TEXT,
    POIID INTEGER,
    VariableID INTEGER,
    FOREIGN KEY (POIID) REFERENCES POI (POIID),
    FOREIGN KEY (VariableID) REFERENCES Variables (VariableID)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
