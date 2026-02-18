"""
Backfill data from multiple stations near Hatboro.
"""
import os
from dotenv import load_dotenv
from src.data.backfill_weathergov import WeatherGovBackfiller
from src.utils.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)

# Top 10 stations near Hatboro
STATIONS = [
    'KPNE',  # Already have this
    'KLOM',
    'KDYL',
    'KTTN',
    'KCKZ',
    'KPHL',
    'KVAY',
    'KUKT',
    'KPTW',
    'KWRI'
]

def backfill_all_stations():
    """Backfill last 7 days from all nearby stations."""
    
    logger.info("=" * 70)
    logger.info("🌫️  MULTI-STATION BACKFILL")
    logger.info("=" * 70)
    logger.info(f"Backfilling {len(STATIONS)} stations")
    logger.info("=" * 70)
    
    total_inserted = 0
    
    for i, station_id in enumerate(STATIONS, 1):
        logger.info(f"\n[{i}/{len(STATIONS)}] Processing {station_id}...")
        logger.info("-" * 70)
        
        try:
            backfiller = WeatherGovBackfiller(station_id)
            backfiller.backfill(days_back=7)
            
            # Track progress (you could parse the logger output, but this is simpler)
            logger.info(f"✅ {station_id} complete")
            
        except Exception as e:
            logger.error(f"❌ {station_id} failed: {e}")
    
    logger.info("\n" + "=" * 70)
    logger.info("MULTI-STATION BACKFILL COMPLETE")
    logger.info("=" * 70)


if __name__ == '__main__':
    backfill_all_stations()