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

CREATE TABLE fq_anonymized_user (
    id INTEGER PRIMARY KEY,
    checkin_count INTEGER
);

CREATE TABLE wu_weather (
    id INTEGER PRIMARY KEY,
    city VARCHAR(100),
    country VARCHAR(100),
    date_time TIMESTAMP WITH TIME ZONE,
    temperature_fahrenheit DECIMAL(5,2),
    temperature_celsius DECIMAL(5,2),
    dew_point DECIMAL(5,2),
    humidity INTEGER,
    wind_speed DECIMAL(5,2),
    wind_gust DECIMAL(5,2),
    direction VARCHAR(20),
    visibility DECIMAL(5,2),
    pressure DECIMAL(5,2),
    wind_chill DECIMAL(5,2),
    heat_index DECIMAL(5,2),
    precipitation DECIMAL(5,2),
    condition VARCHAR(30),
    fog BOOLEAN,
    rain BOOLEAN,
    snow BOOLEAN,
    hail BOOLEAN,
    thunder BOOLEAN,
    tornado BOOLEAN
);

CREATE TABLE geo_country (
    id serial PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(2) NOT NULL
);

CREATE TABLE geo_city (
    id serial PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    city_center geometry(Point,4326),
    state VARCHAR(200),
    country_id INTEGER REFERENCES geo_country(id)
);

CREATE TABLE fq_venue (
    id serial PRIMARY KEY,
    parent_id INTEGER REFERENCES fq_venue(id) DEFAULT NULL,
    foursquare_id VARCHAR(30) UNIQUE NOT NULL,
    date_time_updated TIMESTAMP WITH TIME ZONE,

    geom geometry(Point,4326) NOT NULL,
    city_id INTEGER REFERENCES geo_city(id),
    address VARCHAR(300),
    postal_code VARCHAR(15),
    time_zone VARCHAR(50),

    name VARCHAR(250),
    phone VARCHAR(50),
    twitter VARCHAR(100),
    instagram VARCHAR(100),
    facebook VARCHAR(100),
    url VARCHAR(300),
    verified BOOLEAN,
    created_at TIMESTAMP WITHOUT TIME ZONE,

    checkins_count INTEGER,
    likes_count INTEGER,
    users_count INTEGER,
    tips_count INTEGER,
    photos_count INTEGER,
    listed_count INTEGER,
    
    rating DECIMAL(3,1),
    price_tier INTEGER,
    hours TEXT,
    popular_hours TEXT,
    attributes TEXT,

    atm BOOLEAN,
    coat_check BOOLEAN,
    outdoor_seating BOOLEAN,
    credit_cards BOOLEAN,
    smoking BOOLEAN,
    restroom BOOLEAN,
    music BOOLEAN,
    music_live BOOLEAN,
    music_jukebox BOOLEAN,
    wheelchair_accessible BOOLEAN,
    tvs BOOLEAN,
    wifi BOOLEAN,
    wifi_paid BOOLEAN,
    parking BOOLEAN,
    parking_type VARCHAR(15),
    reservations_nongroup BOOLEAN,
    reservations_group BOOLEAN,
    private_room BOOLEAN,
    dining_delivery BOOLEAN,
    dining_drive_thru BOOLEAN,
    dining_bar_service BOOLEAN,
    dining_table_service BOOLEAN,
    dining_take_out BOOLEAN,
    menu_breakfast BOOLEAN,
    menu_lunch BOOLEAN,
    menu_brunch BOOLEAN,
    menu_dinner BOOLEAN,
    menu_dessert BOOLEAN,
    menu_happy_hour BOOLEAN,
    menu_bar_snacks BOOLEAN,
    drinks_beer BOOLEAN,
    drinks_cocktails BOOLEAN,
    drinks_wine BOOLEAN,
    drinks_full_bar BOOLEAN
);

CREATE TABLE fq_category (
    id serial PRIMARY KEY,
    parent_category INTEGER REFERENCES fq_category(id),
    root_category INTEGER REFERENCES fq_category(id) DEFAULT NULL,
    foursquare_id VARCHAR(30) NOT NULL,
    name VARCHAR(200),
    plural_name VARCHAR(200),
    short_name VARCHAR(200),
    icon_prefix VARCHAR(200),
    icon_suffix VARCHAR(10)
);

CREATE TABLE fq_venue_category (
    venue_id INT REFERENCES fq_venue(id) NOT NULL,
    category_id INT REFERENCES fq_category(id) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT false,
    PRIMARY KEY(venue_id, category_id)
);

CREATE TABLE fq_checkin (
    id serial PRIMARY KEY,
    anonymized_user_id INTEGER REFERENCES fq_anonymized_user(id) NOT NULL,
    date_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    utc_offset INTEGER NOT NULL,
    venue_id INTEGER REFERENCES fq_venue(id) NOT NULL,
    weather_id INTEGER REFERENCES wu_weather(id)   
);
