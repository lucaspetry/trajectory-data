## Foursquare Global Dataset

These scripts were developed for handling the Foursquare global-scale check-in dataset available [here](https://sites.google.com/site/yangdingqi/home/foursquare-dataset).
The scripts create the schema for a PostgreSQL database, import the check-in data and get venue details from the Foursquare API.

### The dataset

The dataset contains 33,278,683 check-ins made by 266,909 users on 3,680,126 Foursquare venues. The data is from April 2012 to September 2013 and includes 415 cities in 77 countries around the world.

### Usage

```
Example: python3 config_database.py config.ini op params
Valid operations:
            create  -  creates the database schema and populates basic info (no params)
            drop    -  drops the database schema (no params)
            init    -  imports data from file to database (params = poi_file checkin_file)
            update  -  update venue information from Foursquare API (params = reset/resume)    
```

The full creation and initialization of the database would be:
```
python3 config_database.py config.ini drop
python3 config_database.py config.ini create
python3 config_database.py config.ini init poi_file checkin_file
python3 config_database.py config.ini update reset
```

### Sample config file (config.ini)

```
[DATABASE]
NAME=my_db_name
HOST=localhost
USER=my_user
PASS=my_pass

[FOURSQUARE_API]
CLIENT_ID=my_client_id
CLIENT_SECRET=my_client_secret
V=20180601
PREMIUM_CALLS=my_premium_calls_limit
REGULAR_CALLS=my_regular_calls_limit
VENUE_ENDPOINT=https://api.foursquare.com/v2/venues/VENUE_ID
CATEGORY_ENDPOINT=https://api.foursquare.com/v2/venues/categories
```
