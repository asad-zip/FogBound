"""
Test NOAA CDO API to find available data for our location.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('NOAA_API_TOKEN')
headers = {'token': token}
base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2"

print("Testing NOAA CDO API access...\n")
print(f"Using token: {token[:10]}..." if token else "ERROR: No token found!")
print()

# Test 1: Check available datasets
print("=" * 70)
print("AVAILABLE DATASETS")
print("=" * 70)
response = requests.get(f"{base_url}/datasets", headers=headers, params={'limit': 50})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    datasets = response.json().get('results', [])
    print(f"Found {len(datasets)} datasets\n")
    for ds in datasets[:10]:  # Show first 10
        print(f"ID: {ds['id']}")
        print(f"  Name: {ds['name']}")
        print(f"  Coverage: {ds.get('mindate')} to {ds.get('maxdate')}")
        print()
else:
    print(f"Error: {response.text}\n")

# Test 2: Search for stations near Hatboro using extent parameter
print("=" * 70)
print("STATIONS NEAR HATBORO (40.1709, -75.1088)")
print("=" * 70)

# Create a bounding box around Hatboro (roughly 10 mile radius)
# Format: minlat,minlon,maxlat,maxlon
extent = "40.0709,-75.2088,40.2709,-75.0088"

params = {
    'extent': extent,
    'limit': 20,
    'startdate': '2025-08-01',
    'enddate': '2026-02-12'
}

response = requests.get(f"{base_url}/stations", headers=headers, params=params)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    stations = data.get('results', [])
    print(f"Found {len(stations)} stations in area\n")
    
    for station in stations[:10]:
        print(f"ID: {station['id']}")
        print(f"  Name: {station['name']}")
        print(f"  Elevation: {station.get('elevation', 'N/A')}m")
        print(f"  Coverage: {station.get('mindate')} to {station.get('maxdate')}")
        print()
else:
    print(f"Error: {response.text}\n")

# Test 3: Check what data types are available for a common dataset
print("=" * 70)
print("DATA TYPES AVAILABLE (first 30)")
print("=" * 70)

response = requests.get(f"{base_url}/datatypes", headers=headers, params={'limit': 30})
print(f"Status: {response.status_code}")

if response.status_code == 200:
    datatypes = response.json().get('results', [])
    print(f"Found {len(datatypes)} data types\n")
    for dt in datatypes:
        print(f"{dt['id']}: {dt.get('name', 'N/A')}")
else:
    print(f"Error: {response.text}\n")