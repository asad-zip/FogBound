-- Weather Observations Table
-- Stores hourly weather data from Weather.gov stations

CREATE TABLE IF NOT EXISTS weather_observations (
    id SERIAL PRIMARY KEY,
    
    -- Metadata
    observed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    station_id VARCHAR(10) NOT NULL,
    station_name VARCHAR(100),
    
    -- Temperature (Celsius)
    temperature_c DECIMAL(5, 2),
    dewpoint_c DECIMAL(5, 2),
    dewpoint_spread_c DECIMAL(5, 2), -- temp - dewpoint (important for fog)
    
    -- Humidity & Pressure
    relative_humidity DECIMAL(5, 2), -- percentage
    barometric_pressure DECIMAL(7, 2), -- pascals
    
    -- Visibility (meters) - KEY FOG INDICATOR
    visibility_m DECIMAL(8, 2),
    
    -- Wind
    wind_speed_kmh DECIMAL(5, 2),
    wind_direction VARCHAR(10), -- 'NW', 'SE', etc.
    wind_gust_kmh DECIMAL(5, 2),
    
    -- Conditions
    conditions_text VARCHAR(100), -- 'Cloudy', 'Fog', 'Clear', etc.
    
    -- Cloud cover (if available)
    cloud_coverage VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(station_id, observed_at) -- Prevent duplicate observations
);

-- Indexes for fast queries
CREATE INDEX idx_observed_at ON weather_observations(observed_at DESC);
CREATE INDEX idx_station_id ON weather_observations(station_id);
CREATE INDEX idx_visibility ON weather_observations(visibility_m);

-- Index for time-series queries
CREATE INDEX idx_station_time ON weather_observations(station_id, observed_at DESC);