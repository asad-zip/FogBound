import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# get coords from .env
lat = os.getenv('LATITUDE')
lon = os.getenv('LONGITUDE')

print(f"Testing Weather.gov API for {lat}, {lon}")
print("-" * 50)

# 1-  get forecast grid point 
points_url = f"https://api.weather.gov/points/{lat},{lon}"
print(f"\n1. Fetching grid point info...")
print(f"    URL: {points_url}")

response = requests.get(points_url, headers={
    'User-Agent': 'Fogbound Weather App (your.email@example.com)'
})

if response.status_code == 200:
    data = response.json()

    # extract imp URLs
    forecast_hourly_url = data['properties']['forecastHourly']
    forecast_url = data['properties']['forecast']
    observation_stations_url = data['properties']['observationStations']
    
    print("Success!")
    print(f"\n   Grid ID: {data['properties']['gridId']}")
    print(f"   Grid X: {data['properties']['gridX']}")
    print(f"   Grid Y: {data['properties']['gridY']}")

    # 2- get hourly forecast
    print(f"\n2. Fetching hourly forecast...")
    forecast_response = requests.get(forecast_hourly_url, headers={
        'User-Agent': 'Fogbound Weather App (your.email@example.com)'
    })
    
    if forecast_response.status_code == 200:
        forecast_data = forecast_response.json()
        periods = forecast_data['properties']['periods'][:3] # first 3hrs
        
        print(" Got hourly forecast!")
        print("\n   Next 3 hours:")
        for period in periods:
            print(f"\n   {period['startTime']}")
            print(f"   Temp: {period['temperature']}°{period['temperatureUnit']}")
            print(f"   Wind: {period['windSpeed']} {period['windDirection']}")
            print(f"   Conditions: {period['shortForecast']}")
            if 'dewpoint' in period:
                print(f"   Dewpoint: {period['dewpoint']}")
            if 'relativeHumidity' in period:
                print(f"   Humidity: {period['relativeHumidity']['value']}%")
  
  
    # 3- get observation stations
    print(f"\n3. Finding nearby weather stations...")
    stations_response = requests.get(observation_stations_url, headers={
        'User-Agent': 'Fogbound Weather App (your.email@example.com)'
    })
    
    if stations_response.status_code == 200:
        stations_data = stations_response.json()
        stations = stations_data['features'][:3]  # first 3 stations
        
        print(f" Found {len(stations_data['features'])} stations nearby!")
        print("\n   Closest stations:")
        for station in stations:
            props = station['properties']
            print(f"\n   {props['name']}")
            print(f"   Station ID: {props['stationIdentifier']}")
        
        # get current observation from nearest station
        if stations:
            station_id = stations[0]['properties']['stationIdentifier']
            obs_url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
            
            print(f"\n4. Getting current observation from {station_id}...")
            obs_response = requests.get(obs_url, headers={
                'User-Agent': 'Fogbound Weather App (your.email@example.com)'
            })

            if obs_response.status_code == 200:
                obs_data = obs_response.json()
                props = obs_data['properties']
                
                print("Current conditions:")
                print(f"\n   Temperature: {props['temperature']['value']}°C")
                print(f"   Dewpoint: {props['dewpoint']['value']}°C")
                print(f"   Humidity: {props['relativeHumidity']['value']}%")
                print(f"   Visibility: {props['visibility']['value']} meters")
                print(f"   Conditions: {props['textDescription']}")
                
                # FOG CHECK!
                visibility_m = props['visibility']['value']
                if visibility_m and visibility_m < 1000:
                    print("\n   🌫️  FOG DETECTED! (Visibility < 1km)")
                else:
                    print("\n   ✅ No fog (Good visibility)")

else:
    print(f"   ❌ Error: {response.status_code}")
    print(f"   {response.text}")


            
