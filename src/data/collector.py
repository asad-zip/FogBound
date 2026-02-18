"""
Automated weather data collector.
Fetches observations from multiple stations and stores them in the database.
"""
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from src.data.fetch_weather import WeatherFetcher
from src.data.database import insert_observation
from src.utils.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)

# Stations to collect from (prioritized by proximity to Hatboro)
STATIONS = [
    'KPNE',  # 9.1 mi
    'KLOM',  # 11.2 mi
    'KDYL',  # 11.0 mi
    'KTTN',  # 21.4 mi
    'KCKZ',  # 19.6 mi
    'KPHL',  # 22.1 mi
    'KVAY',  # 24.4 mi
    'KUKT',  # 26.2 mi
    'KPTW',  # 31.1 mi
    'KWRI'   # 36.7 mi
]


class MultiStationCollector:
    """
    Manages automated weather data collection from multiple stations.
    """
    
    def __init__(self, stations: list, interval_minutes: int = 60):
        """
        Initialize the multi-station collector.
        
        Args:
            stations: List of station IDs to collect from
            interval_minutes: How often to collect full round (default: 60 minutes)
        """
        self.stations = stations
        self.interval_seconds = interval_minutes * 60
        self.fetchers = {station: WeatherFetcher(station) for station in stations}
        
        logger.info(f"MultiStationCollector initialized")
        logger.info(f"Stations: {len(stations)}")
        logger.info(f"Collection interval: {interval_minutes} minutes (full round)")
    
    def collect_all_stations(self) -> dict:
        """
        Fetch and store observations from all stations.
        
        Returns:
            Dictionary with success/failure counts
        """
        stats = {
            'successful': 0,
            'duplicates': 0,
            'failed': 0
        }
        
        for station_id in self.stations:
            try:
                success = self._collect_station(station_id)
                if success:
                    stats['successful'] += 1
                else:
                    stats['failed'] += 1
                    
            except Exception as e:
                logger.error(f"{station_id}: Unexpected error - {e}")
                stats['failed'] += 1
            
            # Small delay between stations to be nice to API
            time.sleep(2)
        
        return stats
    
    def _collect_station(self, station_id: str) -> bool:
        """
        Fetch and store a single observation from one station.
        
        Returns:
            True if successful, False otherwise
        """
        fetcher = self.fetchers[station_id]
        
        # Fetch observation
        observation = fetcher.fetch_latest_observation()
        
        if observation is None:
            logger.error(f"{station_id}: Failed to fetch observation")
            return False
        
        # Validate data
        if not fetcher.validate_observation(observation):
            logger.error(f"{station_id}: Observation failed validation")
            return False
        
        # Insert into database
        try:
            db_observation = insert_observation(observation)
            logger.info(f"{station_id}: ✅ Saved observation from {db_observation.observed_at}")
            
            # Log fog detection
            visibility = observation.get('visibility_m')
            if visibility and visibility < 1000:
                logger.warning(f"{station_id}: 🌫️ FOG DETECTED! Visibility: {visibility}m")
            
            return True
            
        except Exception as e:
            # Check if it's a duplicate
            if 'duplicate key value' in str(e).lower() or 'uix_station_time' in str(e).lower():
                logger.info(f"{station_id}: ⏭️  Observation already exists (skipping)")
                return True  # Not a failure, just already have it
            else:
                logger.error(f"{station_id}: Database error - {e}")
                return False
    
    def run_continuous(self):
        """
        Run the collector continuously, fetching from all stations at regular intervals.
        Press Ctrl+C to stop.
        """
        logger.info("=" * 70)
        logger.info("🌫️  FOGBOUND MULTI-STATION COLLECTOR STARTED")
        logger.info("=" * 70)
        logger.info(f"Stations: {', '.join(self.stations)}")
        logger.info(f"Interval: {self.interval_seconds / 60} minutes per round")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 70)
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                start_time = datetime.now()
                
                logger.info(f"\n{'=' * 70}")
                logger.info(f"COLLECTION CYCLE #{cycle_count} - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'=' * 70}")
                
                # Collect from all stations
                stats = self.collect_all_stations()
                
                # Summary
                logger.info(f"\n{'─' * 70}")
                logger.info(f"Cycle #{cycle_count} Complete:")
                logger.info(f"  ✅ Successful: {stats['successful']}/{len(self.stations)}")
                logger.info(f"  ⏭️  Duplicates: {stats['duplicates']}")
                logger.info(f"  ❌ Failed: {stats['failed']}")
                logger.info(f"{'─' * 70}")
                
                # Wait for next interval
                logger.info(f"\nNext collection in {self.interval_seconds / 60} minutes...")
                logger.info(f"{'=' * 70}\n")
                time.sleep(self.interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 70)
            logger.info("🛑 Collector stopped by user")
            logger.info(f"Total cycles completed: {cycle_count}")
            logger.info("=" * 70)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise


def main():
    """
    Main entry point for the multi-station collector.
    """
    collector = MultiStationCollector(STATIONS, interval_minutes=60)
    collector.run_continuous()


if __name__ == '__main__':
    main()