-- Enable PostGIS (includes raster)
CREATE EXTENSION IF NOT EXISTS postgis;
-- Enable Topology
CREATE EXTENSION IF NOT EXISTS postgis_topology;
-- fuzzy matching needed for Tiger
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
-- rule based standardizer
CREATE EXTENSION IF NOT EXISTS address_standardizer;
-- example rule data set
CREATE EXTENSION IF NOT EXISTS address_standardizer_data_us;
-- Enable US Tiger Geocoder
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

CREATE TABLE go_user (
    id INTEGER PRIMARY KEY,
    checkin_count INTEGER DEFAULT 0,
    friend_count INTEGER DEFAULT 0
);

CREATE TABLE go_friendship (
    user_id INTEGER REFERENCES go_user(id) NOT NULL,
    friend_id INTEGER REFERENCES go_user(id) NOT NULL
);
ALTER TABLE go_friendship ADD CONSTRAINT "ID_PKEY" PRIMARY KEY (user_id, friend_id);

CREATE TABLE go_checkin (
    id serial PRIMARY KEY,
    user_id INTEGER REFERENCES go_user(id) NOT NULL,
    geom geometry(Point,4326) NOT NULL,
    location_id VARCHAR(100) NOT NULL,
    date_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    utc_offset INTEGER NOT NULL
);
