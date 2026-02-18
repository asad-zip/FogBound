"""
Find all Weather.gov stations near Hatboro for multi-station training.
"""
import requests

headers = {
    'User-Agent': 'Fogbound Weather App',
    'Accept': 'application/json'
}

# Hatboro coordinates
lat, lon = 40.1709, -75.1088

print("Finding Weather.gov stations near Hatboro...\n")

# Get stations from Weather.gov
url = f"https://api.weather.gov/points/{lat},{lon}/stations"
response = requests.get(url, headers=headers, timeout=10)

if response.status_code == 200:
    data = response.json()
    stations = data.get('features', [])
    
    print(f"Found {len(stations)} stations\n")
    print("=" * 70)
    
    for i, station in enumerate(stations[:15], 1):  # Show top 15
        props = station['properties']
        coords = station['geometry']['coordinates']
        
        station_id = props['stationIdentifier']
        name = props['name']
        
        print(f"{i}. {station_id} - {name}")
        print(f"   Coordinates: {coords[1]:.4f}, {coords[0]:.4f}")
        
        # Calculate rough distance (not accurate but good enough)
        lat_diff = abs(coords[1] - lat)
        lon_diff = abs(coords[0] - lon)
        distance_approx = ((lat_diff**2 + lon_diff**2)**0.5) * 69  # miles
        
        print(f"   Distance: ~{distance_approx:.1f} miles")
        print()
else:
    print(f"Error: {response.status_code}")