"""
Weather data fetcher for Weather.gov API.
"""
import os
import requests
from datetime import datetime
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class WeatherFetcher:
    
    def __init__(self, station_id: str):

        self.station_id = station_id
        self.base_url = "https://api.weather.gov"
        self.headers = {
            'User-Agent': 'Fogbound Weather App (github.com/asad-zip/FogBound)',
            'Accept': 'application/json'
        }
    
    def fetch_latest_observation(self) -> Optional[Dict]:
        url = f"{self.base_url}/stations/{self.station_id}/observations/latest"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  
            
            data = response.json()
            
            # parse and transform the data
            observation = self._parse_observation(data)
            return observation
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def _parse_observation(self, api_response: Dict) -> Dict:
        """
        Parse Weather.gov API response into database-ready format.
        
        Args:
            api_response: Raw JSON response from Weather.gov
            
        Returns:
            Dictionary with keys matching WeatherObservation model
        """
        properties = api_response.get('properties', {})
        
        # extract timestamp
        timestamp_str = properties.get('timestamp')
        observed_at = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        # extract tempe values (convert from Celsius - API returns in C)
        temp_c = self._extract_value(properties.get('temperature'))
        dewpoint_c = self._extract_value(properties.get('dewpoint'))
        
        # calculate dewpoint spread (fog indicator)
        dewpoint_spread_c = None
        if temp_c is not None and dewpoint_c is not None:
            dewpoint_spread_c = round(temp_c - dewpoint_c, 2)
        
        # extract other values
        humidity = self._extract_value(properties.get('relativeHumidity'))

        # barometric pressure (convert from pascals to hectopascals)
        pressure_pa = self._extract_value(properties.get('barometricPressure'))
        pressure = None
        if pressure_pa is not None:
            pressure = round(pressure_pa / 100, 2)  # Pa to hPa (or mb)

        visibility = self._extract_value(properties.get('visibility'))
        
        # wind (convert from m/s to km/h)
        wind_speed_ms = self._extract_value(properties.get('windSpeed'))
        wind_speed_kmh = None
        if wind_speed_ms is not None:
            wind_speed_kmh = round(wind_speed_ms * 3.6, 2)
        
        wind_gust_ms = self._extract_value(properties.get('windGust'))
        wind_gust_kmh = None
        if wind_gust_ms is not None:
            wind_gust_kmh = round(wind_gust_ms * 3.6, 2)
        
        # wind direction (convert from degrees to cardinal)
        wind_direction_deg = self._extract_value(properties.get('windDirection'))
        wind_direction = self._degrees_to_cardinal(wind_direction_deg) if wind_direction_deg else None
        
        # text description
        conditions = properties.get('textDescription', '')
        
        # cloud coverage (if available)
        cloud_layers = properties.get('cloudLayers', [])
        cloud_coverage = None
        if cloud_layers and len(cloud_layers) > 0:
            cloud_coverage = cloud_layers[0].get('amount', '')
        
        # station info
        station = api_response.get('properties', {}).get('station', '')
        station_id = station.split('/')[-1] if station else self.station_id
        
        return {
            'observed_at': observed_at,
            'station_id': station_id,
            'station_name': properties.get('station', ''),
            'temperature_c': temp_c,
            'dewpoint_c': dewpoint_c,
            'dewpoint_spread_c': dewpoint_spread_c,
            'relative_humidity': humidity,
            'barometric_pressure': pressure,
            'visibility_m': visibility,
            'wind_speed_kmh': wind_speed_kmh,
            'wind_direction': wind_direction,
            'wind_gust_kmh': wind_gust_kmh,
            'conditions_text': conditions,
            'cloud_coverage': cloud_coverage
        }
    
    def _extract_value(self, field: Optional[Dict]) -> Optional[float]:
        if field is None:
            return None
        
        value = field.get('value')
        if value is None:
            return None
        
        return round(float(value), 2)
    
    def _degrees_to_cardinal(self, degrees: float) -> str:
        """
        Convert wind direction from degrees to cardinal direction.
        
        Args:
            degrees: Wind direction in degrees (0-360)
            
        Returns:
            Cardinal direction (N, NE, E, SE, S, SW, W, NW)
        """
        if degrees is None:
            return None
        
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = round(degrees / 45) % 8
        return directions[index]
    
    def validate_observation(self, observation: Dict) -> bool:
        """
        Validate observation data before inserting into database.
        
        Args:
            observation: Dictionary with observation data
            
        Returns:
            True if valid, False otherwise
        """
        # check required fields
        if not observation.get('observed_at'):
            print("❌ Validation failed: missing observed_at")
            return False
        
        if not observation.get('station_id'):
            print("❌ Validation failed: missing station_id")
            return False
        
        # validate temperature range (-50 to 50°C)
        temp = observation.get('temperature_c')
        if temp is not None and (temp < -50 or temp > 50):
            print(f"❌ Validation failed: temperature {temp}°C out of range")
            return False
        
        # validate humidity (0-100%)
        humidity = observation.get('relative_humidity')
        if humidity is not None and (humidity < 0 or humidity > 100):
            print(f"❌ Validation failed: humidity {humidity}% out of range")
            return False
        
        # validate visibility (positive number)
        visibility = observation.get('visibility_m')
        if visibility is not None and visibility < 0:
            print(f"❌ Validation failed: visibility {visibility}m is negative")
            return False
        
        return True


"""Quick test of the WeatherFetcher."""
def test_fetcher():
    print("Testing WeatherFetcher...")
    
    fetcher = WeatherFetcher('KPNE')
    observation = fetcher.fetch_latest_observation()
    
    if observation:
        print("✅ Fetch successful!")
        print(f"\nObservation data:")
        for key, value in observation.items():
            print(f"  {key}: {value}")
        
        print(f"\n🌫️ Fog check:")
        visibility = observation.get('visibility_m')
        if visibility and visibility < 1000:
            print(f"  FOG DETECTED! Visibility: {visibility}m")
        else:
            print(f"  No fog. Visibility: {visibility}m")
        
        # test validation
        print(f"\n✅ Validation: {fetcher.validate_observation(observation)}")
    else:
        print("❌ Fetch failed")


if __name__ == '__main__':
    test_fetcher()