import pandas as pd
import json
import os
import re
from geopy.distance import great_circle
# File paths
csv_file = "SensorData1.csv"
json_file = "SensorData2.json"

# Check if files exist
if not os.path.exists(csv_file):
    raise FileNotFoundError(f"CSV file '{csv_file}' not found.")
if not os.path.exists(json_file):
    raise FileNotFoundError(f"JSON file '{json_file}' not found.")

# Load CSV sensor data
csv_data = pd.read_csv(csv_file)

# Function to clean numeric columns
def clean_numeric(value):
    value = re.sub(r"[^0-9.-]", "", str(value))  # Remove non-numeric characters
    try:
        return float(value)
    except ValueError:
        return None  # Return None for invalid values

# Apply cleaning to latitude and longitude
csv_data["latitude"] = csv_data["latitude"].apply(clean_numeric)
csv_data["longitude"] = csv_data["longitude"].apply(clean_numeric)

# Drop rows with invalid coordinates
csv_data = csv_data.dropna()

# Filter invalid coordinates
csv_data = csv_data[(csv_data["latitude"].between(-90, 90)) & (csv_data["longitude"].between(-180, 180))]

# Load JSON sensor data
with open(json_file, "r") as file:
    json_data = json.load(file)
    cleaned_json_data = []
    for row in json_data:
        row["latitude"] = clean_numeric(row["latitude"])
        row["longitude"] = clean_numeric(row["longitude"])
        if -90 <= row["latitude"] <= 90 and -180 <= row["longitude"] <= 180:
            cleaned_json_data.append(row)
# Replace with cleaned JSON data
json_data = cleaned_json_data

# Debugging: Print data types and sample data
print(csv_data.dtypes)
print(csv_data.head())
print(json_data[:3])  # Print first 3 rows for validation

###PREVIOUS ATTEMPT WITH ABOSULTE VALUES
# Function to check if two locations are within 100 meters (approx 0.0009 degrees latitude/longitude)
# def is_within_100m(lat1, lon1, lat2, lon2):
#     return abs(lat1 - lat2) <= 0.0009 and abs(lon1 - lon2) <= 0.0009

# Function to check if two locations are within 100 meters using great-circle distance
def is_within_100m(lat1, lon1, lat2, lon2):
    return great_circle((lat1, lon1), (lat2, lon2)).meters <= 100

# Find matching pairs of sensor readings
matches = {}
for _, csv_row in csv_data.iterrows():
    csv_id = int(csv_row["id"])  # Ensure integer ID
    csv_lat, csv_lon = csv_row["latitude"], csv_row["longitude"]
    
    for json_row in json_data:
        json_id = int(json_row["id"])  # Ensure integer ID
        json_lat, json_lon = json_row["latitude"], json_row["longitude"]
        
        if is_within_100m(csv_lat, csv_lon, json_lat, json_lon):
            matches[csv_id] = json_id

# Save results
# Save results as JSON
output_file = "SensorOutput.json"
with open(output_file, "w") as json_out:
    json.dump(matches, json_out, indent=4)

print(f"Matched IDs saved to {output_file}")