from src.data.database import get_recent_observations

observations = get_recent_observations('KPNE', limit=5)
print(f"Found {len(observations)} observations:\n")

for obs in observations:
    print(f"Time: {obs.observed_at}")
    print(f"  Temp: {obs.temperature_c}°C")
    print(f"  Pressure: {obs.barometric_pressure} hPa")
    print(f"  Visibility: {obs.visibility_m}m")
    print(f"  Fog? {'YES 🌫️' if obs.visibility_m and obs.visibility_m < 1000 else 'No'}")
    print()