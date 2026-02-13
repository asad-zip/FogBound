"""
Database connection and models for Fogbound weather data.
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

Base = declarative_base()

# connection URL
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)



class WeatherObservation(Base):
    """
    SQLAlchemy model for weather observations table.
    Represents a single weather reading from a station at a specific time.
    """
   
    __tablename__ = 'weather_observations'
    
    id = Column(Integer, primary_key=True)
    
    # metadata
    observed_at = Column(DateTime(timezone=True), nullable=False)
    station_id = Column(String(10), nullable=False)
    station_name = Column(String(100))
    
    # temp (Celsius)
    temperature_c = Column(Numeric(5, 2))
    dewpoint_c = Column(Numeric(5, 2))
    dewpoint_spread_c = Column(Numeric(5, 2))
    
    # humidity & pressure
    relative_humidity = Column(Numeric(5, 2))
    barometric_pressure = Column(Numeric(7, 2))
    
    # visibility (meters) - KEY FOG INDICATOR
    visibility_m = Column(Numeric(8, 2))
    
    # wind
    wind_speed_kmh = Column(Numeric(5, 2))
    wind_direction = Column(String(10))
    wind_gust_kmh = Column(Numeric(5, 2))
    
    # conditions
    conditions_text = Column(String(100))
    cloud_coverage = Column(String(50))
    
    # timestamp
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # table constraints
    __table_args__ = (
        UniqueConstraint('station_id', 'observed_at', name='uix_station_time'),
    )
    
    def __repr__(self):
        """String representation for debugging."""
        return (
            f"<WeatherObservation(station={self.station_id}, "
            f"time={self.observed_at}, temp={self.temperature_c}°C, "
            f"visibility={self.visibility_m}m)>"
        )


# engine (connection pool to database)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # verify connections before using them
    echo=False  # set to True to see SQL queries 
)

# session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_session():
    """
    Get a new database session.
    
    Usage:
        session = get_session()
        try:
            # do database work
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    """
    return SessionLocal()


def init_db():
    Base.metadata.create_all(bind=engine)
    

def insert_observation(observation_data: dict) -> WeatherObservation:
    """
    Insert a weather observation into the database.
    
    Args:
        observation_data: Dictionary with keys matching WeatherObservation columns
        
    Returns:
        The inserted WeatherObservation object
        
    Raises:
        Exception: If insert fails (e.g., duplicate, database error)
    """
    session = get_session()
    try:
        observation = WeatherObservation(**observation_data)
        session.add(observation)
        session.commit()
        session.refresh(observation)  # get auto-generated ID
        return observation
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_recent_observations(station_id: str, limit: int = 10):
    """
    Get the most recent observations from a station.
    
    Args:
        station_id: Weather station ID (e.g., 'KPNE')
        limit: Number of observations to return
        
    Returns:
        List of WeatherObservation objects, newest first
    """
    session = get_session()
    try:
        observations = (
            session.query(WeatherObservation)
            .filter(WeatherObservation.station_id == station_id)
            .order_by(WeatherObservation.observed_at.desc())
            .limit(limit)
            .all()
        )
        return observations
    finally:
        session.close()
