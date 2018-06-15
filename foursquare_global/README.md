## Foursquare Global Dataset

These scripts were developed for handling the Foursquare global-scale check-in dataset available [here](https://sites.google.com/site/yangdingqi/home/foursquare-dataset).
The scripts create the schema for a PostgreSQL database, import the check-in data and get venue details from the Foursquare API.

### Usage

```
Example: python3 scripts/config_database.py config.ini op params
Valid operations:
    		create  -  creates the database schema and populates basic info (no params)
    		drop    -  drops the database schema (no params)
    		init    -  imports data from file to database (params = poi_file checkin_file)
    		update  -  update venue information from Foursquare API (params = reset/resume)    
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
