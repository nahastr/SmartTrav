import pandas as pd

# Test reading Dining.csv
dining_df = pd.read_csv('data/Dining.csv')
print("Dining.csv columns:", dining_df.columns.tolist())
print("Dining.csv sample:", dining_df.head())

# Test reading Spots.csv
spots_df = pd.read_csv('data/Spots.csv')
print("Spots.csv columns:", spots_df.columns.tolist())
print("Spots.csv sample:", spots_df.head())
