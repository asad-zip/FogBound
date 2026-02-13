"""
Test the collector with a single fetch.
"""
from src.data.collector import WeatherCollector

collector = WeatherCollector('KPNE', interval_minutes=30)
success = collector.collect_once()

if success:
    print("\n✅ Collection test passed!")
else:
    print("\n❌ Collection test failed")