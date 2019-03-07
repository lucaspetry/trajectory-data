## Automatic Identification System (AIS)
- Description: Vessel traffic data collected by the U.S. Coast Guard.
- Folder: `ais`
- Sources:
  - https://marinecadastre.gov/ais/
  - https://marinecadastre.gov/ais/AIS%20Documents/UTMZoneMap2014.png
- Instructions:
  1. **Downloading the data:** AIS data can be downloaded by running the `get_ais_files.py` script.
  Before running it, change the `years`, `months`, and `zones` variables with the specific values for which you want to download the data.
  2. **Processing the data:** `process_ais_files.py` can be used for curating the data. It merges files of different zones into a single file,
  one for each month/year pair. Three new columns are added in the processed files: `Zone` (the zone file from where the record was extracted),
  `VesselTypeGroup` and `VesselTypeDescription` (type information gathered from the `vessel_types.csv` file). Lastly, the data is sorted in ascending
  order by `DateTime` and `IMO`, respectively. Be aware that the files are fully loaded in memory for this last step (I am currently working on sorting
  files using unix sort).

## Local Climatological Data (LCD)
- Description: Hourly observations of temperature, precipitation, sky conditions, etc. The data is collected at stations located on the ground.
- Folder: `lcd`
- Sources:
  - https://www.ncdc.noaa.gov/cdo-web/datatools/lcd
  - ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.csv
- Instructions:
  1. **Downloading the data:** LCD must be manually downloaded from NOAA. When ordering LCD from NOAA, you need to select the stations to retrieve the data for.
  File names must follow the pattern `*_year_month.csv` and must be placed inside the `lcd` folder. The list of stations can also be downloaded from the FTP url
  listed above.
  2. **Processing the data:** The script `process_noaa_stations.py` processes station files. It merges the station information selected on the LCD website with
  the extensive station list available at the FTP url above. Example files are provided in the folder. Following, run the script `process_lcd.py` to process the
  files downloaded. The script extracts and formats hourly information fields in the original files, in order to make them compatible with the AIS data.

## Global Marine Data - International Comprehensive Ocean-Atmosphere Data Set (ICOADS)
- Description: Observations from ships, buoys, or platforms comprising data such as sea level pressure, wind direction and speed, wave data, etc.
- Folder: `icoads`
- Sources:
  - https://www.ncdc.noaa.gov/cdo-web/datatools/marine
- Instructions:
  1. **Downloading the data:** Marine data must be manually downloaded from NOAA. When ordering data from NOAA, you need to select the region to retrieve the data for.
  File names must follow the pattern `*_year.csv` and must be placed inside the `icoads` folder.
  2. **Processing the data:** The script `extract_buoy_information.py` reads through the data files and extracts all distinct buoys/ships that there is. Their ids and the first spatial location found are stored in `processed/icoads_buoys_ships.csv`. `process_icoads.py` processes the data downloaded and merges them into a single file for each year.

-------------
**PS: All scripts must be run from inside their respective folders.**