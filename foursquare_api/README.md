## Foursquare API

This script was developed for retrieving venue details from the [Foursquare API](https://developer.foursquare.com/).

### Usage

```
Example: python3 get_venues.py config.ini
```

### Sample config file (config.ini)

```
[GENERAL]
VENUE_FILE=venue_file.csv
DATA_DIR=data/

[FOURSQUARE_API]
KEYS=CLIENT_ID1,CLIENT_SECRET1;CLIENT_ID2,CLIENT_SECRET2;CLIENT_ID3,CLIENT_SECRET3
DEAD_VENUES=4c193b68838020a14167e561,4d5cc731775f8cfa662bbae0,4d06523fe350b60c03e68c42
V=20180731
VENUE_ENDPOINT=https://api.foursquare.com/v2/venues/VENUE_ID
```

Description:
- `CHECKIN_FILE` is a CSV file containing the venue IDs to fetch from the API. The first column must be the foursquare ID of the venue. Other columns in the CSV file (if any) are ignored;
- `DATA_DIR` is the directory where venues will be saved to;
- `KEYS` are the corresponding API IDs and secrets to use (following the format in the example). Once the quota is reached for a pair of ID and secret, the next one in the list is used, and so on until the end of the list. If the script reaches the end of the list of KEYS, then it will sleep and restart at midnight from the first key pair;
- `DEAD_VENUES` is a list of venue IDs to ignore;
- `V` is the version parameter of the Fourquare API;
- `VENUE_ENDPOINT` is the venue endpoint in which `VENUE_ID` is replaced with the corresponding venue ID being fetched.


### Sample Venue CSV file (venue_file.csv)

```
foursquare_id,count
4b49cb0ff964a520b67326e3,34509
4d8cce87cb9b224bb19c5d41,28767
4b684c69f964a5204f702be3,28631
4b19f917f964a520abe623e3,28086
4b0587a6f964a5203d9e22e3,25163
4ad83e6ff964a520eb1021e3,21492
4b50966af964a520632827e3,20498
4b0587fdf964a52034ab22e3,20312
4cb54fd08db0a14356c36116,19548
4b4f537ef964a5206d0127e3,18853
4be139c2c1732d7f797c5b9a,18804
```