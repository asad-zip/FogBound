"""
Export database to CSV for backup/sharing.
"""
import pandas as pd
from src.data.database import get_session, WeatherObservation

session = get_session()

# Query all observations
observations = session.query(WeatherObservation).all()

# Convert to list of dicts
data = []
for obs in observations:
    data.append({
        'observed_at': obs.observed_at,
        'station_id': obs.station_id,
        'temperature_c': obs.temperature_c,
        'dewpoint_c': obs.dewpoint_c,
        'dewpoint_spread_c': obs.dewpoint_spread_c,
        'relative_humidity': obs.relative_humidity,
        'barometric_pressure': obs.barometric_pressure,
        'visibility_m': obs.visibility_m,
        'wind_speed_kmh': obs.wind_speed_kmh,
        'wind_direction': obs.wind_direction,
        'conditions_text': obs.conditions_text,
        'cloud_coverage': obs.cloud_coverage
    })

# Save to CSV
df = pd.DataFrame(data)
df.to_csv('backups/weather_data.csv', index=False)

print(f"Exported {len(data)} observations to backups/weather_data.csv")

session.close()

# Backups
#backups/
