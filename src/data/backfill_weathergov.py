"""
Backfill historic weather data from Weather.gov API.
Fetches all available hourly observations (typically last 7-10 days).
"""
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.data.fetch_weather import WeatherFetcher
from src.data.database import insert_observation, get_session, WeatherObservation
from src.utils.logger import setup_logger
import requests

load_dotenv()
logger = setup_logger(__name__)


class WeatherGovBackfiller:
    """
    Backfill historic observations from Weather.gov.
    """
    
    def __init__(self, station_id: str):
        self.station_id = station_id
        self.base_url = "https://api.weather.gov"
        self.headers = {
            'User-Agent': 'Fogbound Weather App (github.com/yourname/fogbound)',
            'Accept': 'application/json'
        }
        self.fetcher = WeatherFetcher(station_id)
    
    def backfill(self, days_back: int = 30):
        """
        Backfill all available observations.
        
        Args:
            days_back: Number of days to attempt (default: 30, but API may have less)
        """
        logger.info("=" * 70)
        logger.info("🌫️  WEATHER.GOV HISTORIC DATA BACKFILL")
        logger.info("=" * 70)
        logger.info(f"Station: {self.station_id}")
        logger.info(f"Attempting to fetch last {days_back} days")
        logger.info("=" * 70)
        
        total_fetched = 0
        total_inserted = 0
        total_duplicates = 0
        total_errors = 0
        
        # fetch in chunks (500 record limit per request)
        all_observations = []
        
        # start from 30 days ago, fetch everything available
        start_time = datetime.now() - timedelta(days=days_back)
        
        logger.info(f"\nFetching observations since {start_time.date()}...")
        
        url = f"{self.base_url}/stations/{self.station_id}/observations"
        params = {
            'start': start_time.isoformat() + 'Z',
            'limit': 500
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            features = data.get('features', [])
            total_fetched = len(features)
            
            logger.info(f"Retrieved {total_fetched} observations from API")
            
            if total_fetched == 0:
                logger.warning("No historic data available from Weather.gov")
                return
            
            # show actual date range
            if features:
                oldest = features[-1]['properties']['timestamp']
                newest = features[0]['properties']['timestamp']
                logger.info(f"Date range: {oldest} to {newest}")
            
            # process each observation
            for feature in features:
                try:
                    observation = self._parse_observation(feature)
                    
                    if not observation:
                        total_errors += 1
                        continue
                    
                    if not self.fetcher.validate_observation(observation):
                        total_errors += 1
                        continue
                    
                    insert_observation(observation)
                    total_inserted += 1
                    
                    # log fog events
                    if observation.get('visibility_m') and observation.get('visibility_m') < 1000:
                        logger.warning(f"🌫️ FOG: {observation['observed_at']} - {observation['visibility_m']}m visibility")
                    
                except Exception as e:
                    if 'duplicate key value' in str(e).lower() or 'uix_station_time' in str(e).lower():
                        total_duplicates += 1
                    else:
                        total_errors += 1
                        logger.error(f"Error: {e}")
            
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return
        
        # summary
        logger.info("\n" + "=" * 70)
        logger.info("BACKFILL COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Total observations fetched: {total_fetched}")
        logger.info(f"Successfully inserted: {total_inserted}")
        logger.info(f"Duplicates skipped: {total_duplicates}")
        logger.info(f"Errors: {total_errors}")
        logger.info("=" * 70)
        
        self._show_db_stats()
    
    def _parse_observation(self, feature: dict):
        """Parse Weather.gov observation feature into database format."""
        try:
            properties = feature.get('properties', {})
            fake_response = {'properties': properties}
            observation = self.fetcher._parse_observation(fake_response)
            return observation
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None
    
    def _show_db_stats(self):
        """Show statistics about collected data."""
        session = get_session()
        try:
            total = session.query(WeatherObservation).count()
            
            fog_count = session.query(WeatherObservation).filter(
                WeatherObservation.visibility_m < 1000
            ).count()
            
            first = session.query(WeatherObservation).order_by(
                WeatherObservation.observed_at.asc()
            ).first()
            
            last = session.query(WeatherObservation).order_by(
                WeatherObservation.observed_at.desc()
            ).first()
            
            logger.info("\nDATABASE STATISTICS:")
            logger.info(f"  Total observations: {total}")
            logger.info(f"  Fog events (visibility < 1km): {fog_count}")
            if first and last:
                logger.info(f"  Date range: {first.observed_at} to {last.observed_at}")
                days = (last.observed_at - first.observed_at).days
                logger.info(f"  Coverage: {days} days")
            
        finally:
            session.close()


def main():
    station_id = os.getenv('STATION_ID', 'KPNE')
    backfiller = WeatherGovBackfiller(station_id)
    backfiller.backfill(days_back=30)


if __name__ == '__main__':
    main()