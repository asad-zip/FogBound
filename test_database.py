"""
Quick test to verify database connection and model.
"""
from src.data.database import get_session, insert_observation, get_recent_observations, WeatherObservation
from datetime import datetime

def test_connection():
    """Test that we can connect to the database."""
    session = get_session()
    try:
        # Try a simple query
        count = session.query(WeatherObservation).count()
        print(f"✅ Database connection successful!")
        print(f"   Current observations in database: {count}")
    finally:
        session.close()

def test_insert():
    """Test inserting a dummy observation."""
    test_data = {
        'observed_at': datetime.now(),
        'station_id': 'TEST',
        'station_name': 'Test Station',
        'temperature_c': 10.5,
        'dewpoint_c': 8.0,
        'dewpoint_spread_c': 2.5,
        'relative_humidity': 85.0,
        'visibility_m': 5000.0
    }
    
    try:
        obs = insert_observation(test_data)
        print(f"✅ Insert successful!")
        print(f"   Inserted observation: {obs}")
    except Exception as e:
        print(f"❌ Insert failed: {e}")

def test_query():
    """Test querying recent observations."""
    observations = get_recent_observations('KPNE', limit=5)
    print(f"✅ Query successful!")
    print(f"   Found {len(observations)} recent observations from KPNE")
    for obs in observations:
        print(f"   - {obs}")

if __name__ == '__main__':
    print("Testing database module...\n")
    test_connection()
    print()
    test_insert()
    print()
    test_query()