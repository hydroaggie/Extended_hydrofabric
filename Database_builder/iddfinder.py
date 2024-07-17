import pandas as pd
from scipy.spatial import cKDTree
import numpy as np

file1_path = 'data/ResOpsUS/attributes/reservoir_attributes.csv'
file2_path = 'data/results/filtered_rows.csv'

df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)

df1 = df1.replace([np.inf, -np.inf], np.nan).dropna(subset=['LAT', 'LONG'])
df2 = df2.replace([np.inf, -np.inf], np.nan).dropna(subset=['Latitude', 'Longitude'])

coords1 = df1[['LAT', 'LONG']].values
coords2 = df2[['Latitude', 'Longitude']].values

# using KD-Tree for spatial lookup
tree = cKDTree(coords2)

# Find the closest row
distances, indices = tree.query(coords1)

column_to_copy = 'NID ID'

df1[column_to_copy] = df2.iloc[indices][column_to_copy].values

output_file_path = 'data/results/updated_reservoir_attributes.csv'
df1.to_csv(output_file_path, index=False)