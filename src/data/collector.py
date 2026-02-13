"""
Automated weather data collector.
Fetches observations every 30 minutes and stores them in the database.
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


class WeatherCollector:
    """
    Manages automated weather data collection.
    """
    
    def __init__(self, station_id: str, interval_minutes: int = 30):
        """
        Initialize the weather collector.
        
        Args:
            station_id: Weather station ID (e.g., 'KPNE')
            interval_minutes: How often to collect data (default: 30 minutes)
        """
        self.station_id = station_id
        self.interval_seconds = interval_minutes * 60
        self.fetcher = WeatherFetcher(station_id)
        
        logger.info(f"WeatherCollector initialized for station {station_id}")
        logger.info(f"Collection interval: {interval_minutes} minutes")
    
    def collect_once(self) -> bool:
        """
        Fetch and store a single observation.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Fetching observation from {self.station_id}...")
        
        # fetch observation
        observation = self.fetcher.fetch_latest_observation()
        
        if observation is None:
            logger.error("Failed to fetch observation from API")
            return False
        
        # validate data
        if not self.fetcher.validate_observation(observation):
            logger.error("Observation failed validation")
            return False
        
        # insert into database
        try:
            db_observation = insert_observation(observation)
            logger.info(f"✅ Observation saved: {db_observation.station_id} at {db_observation.observed_at}")
            
            # log fog detection
            visibility = observation.get('visibility_m')
            if visibility and visibility < 1000:
                logger.warning(f"🌫️ FOG DETECTED! Visibility: {visibility}m")
            
            return True
            
        except Exception as e:
            # check if duplicate (this is expected and OK)
            if 'duplicate key value' in str(e).lower() or 'uix_station_time' in str(e).lower():
                logger.info("⏭️  Observation already exists in database (duplicate - skipping)")
                return True
            else:
                logger.error(f"Database error: {e}")
                return False
    
    def run_continuous(self):
        """
        Run the collector continuously, fetching data at regular intervals.
        Press Ctrl+C to stop.
        """
        logger.info("=" * 60)
        logger.info("🌫️  FOGBOUND WEATHER COLLECTOR STARTED")
        logger.info("=" * 60)
        logger.info(f"Station: {self.station_id}")
        logger.info(f"Interval: {self.interval_seconds / 60} minutes")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        try:
            while True:
                # collect data
                start_time = datetime.now()
                success = self.collect_once()
                
                if success:
                    logger.info(f"Collection completed successfully")
                else:
                    logger.warning(f"Collection failed - will retry in {self.interval_seconds / 60} minutes")
                
                # wait for next interval
                logger.info(f"Next collection in {self.interval_seconds / 60} minutes...")
                logger.info("-" * 60)
                time.sleep(self.interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("🛑 Collector stopped by user")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise


def main():
    """
    Main entry point for the collector.
    """
    # Gget station ID from environment or use default
    station_id = os.getenv('STATION_ID', 'KPNE')
    
    # create and run collector
    collector = WeatherCollector(station_id, interval_minutes=30)
    collector.run_continuous()


if __name__ == '__main__':
    main()