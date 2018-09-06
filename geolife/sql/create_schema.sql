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

CREATE TABLE ge_user (
    id INTEGER PRIMARY KEY,
    point_count INTEGER
);

CREATE TABLE ge_transportation (
    id INTEGER PRIMARY KEY,
    mode VARCHAR(20)
);

CREATE TABLE ge_point (
    id serial PRIMARY KEY,
    tid INTEGER NOT NULL,
    user_id INTEGER REFERENCES ge_user(id) NOT NULL,
    geom geometry(Point,4326) NOT NULL,
    altitude INTEGER DEFAULT -999,
    date_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    utc_offset INTEGER NOT NULL,
    transportation_id INTEGER REFERENCES ge_transportation(id) DEFAULT NULL
);
