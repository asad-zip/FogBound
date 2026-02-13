"""
Test Weather.gov historic observations availability.
"""
import requests
from datetime import datetime, timedelta

headers = {
    'User-Agent': 'Fogbound Weather App (github.com/yourname/fogbound)',
    'Accept': 'application/json'
}

base_url = "https://api.weather.gov"
station_id = "KPNE"

print("Testing Weather.gov historic data availability...\n")

# Test how far back we can get data
test_dates = [
    ("1 day ago", 1),
    ("1 week ago", 7),
    ("2 weeks ago", 14),
    ("1 month ago", 30),
    ("3 months ago", 90),
    ("6 months ago", 180)
]

for label, days_back in test_dates:
    start = datetime.now() - timedelta(days=days_back)
    start_iso = start.isoformat() + "Z"
    
    url = f"{base_url}/stations/{station_id}/observations"
    params = {
        'start': start_iso,
        'limit': 1  # Just need to see if data exists
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            features = data.get('features', [])
            
            if features:
                obs_time = features[0]['properties']['timestamp']
                print(f"✅ {label:15} - Data available (sample: {obs_time})")
            else:
                print(f"❌ {label:15} - No data found")
        else:
            print(f"❌ {label:15} - API error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ {label:15} - Error: {e}")

# Test pagination - how many records can we get?
print("\n" + "=" * 70)
print("Testing record limits...")
print("=" * 70)

start = datetime.now() - timedelta(days=7)
start_iso = start.isoformat() + "Z"

url = f"{base_url}/stations/{station_id}/observations"
params = {
    'start': start_iso,
    'limit': 500  # Max allowed
}

response = requests.get(url, headers=headers, params=params, timeout=10)

if response.status_code == 200:
    data = response.json()
    features = data.get('features', [])
    print(f"Requested last 7 days, got {len(features)} observations")
    
    if features:
        first = features[-1]['properties']['timestamp']
        last = features[0]['properties']['timestamp']
        print(f"Date range: {first} to {last}")
else:
    print(f"Error: {response.status_code}")