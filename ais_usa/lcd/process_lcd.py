import glob
import os
import pandas as pd
from datetime import datetime
from datetime import timedelta


file_pattern = ':dir/*:year_:month.csv'
proc_dir = 'processed/'
station_file = proc_dir + 'lcd_station_usa_west_coast.csv'
years = ['2015']
months = ['01', '02', '03', '04', '05', '06',
          '07', '08', '09', '10', '11', '12']


if not os.path.isfile(station_file):
    print('Please run process_noaa_stations.py first!')
    exit()

stations = pd.read_csv(station_file)

if not os.path.isdir(proc_dir):
    os.mkdir(proc_dir)

for year in years:
    for month in months:
        pattern = file_pattern.replace(':dir', '.') \
                              .replace(':year', year) \
                              .replace(':month', month)
        files = glob.glob(pattern)

        for file in files:
            print('Processing file', file)
            proc_file = file.replace('./', proc_dir)
            df = pd.read_csv(file)
            new_df = pd.DataFrame()
            new_df['usaf'] = [str(s)[:6] for s in df['STATION'].values]
            new_df['wban'] = [int(str(s)[6:]) for s in df['STATION'].values]

            utc_offset = []
            (icao, station, state, country,
             lat, lon, elev_meters) = [], [], [], [], [], [], []

            for w in new_df['wban'].values:
                utc_offset.append(timedelta(minutes=stations.loc[
                    stations['wban'] == w, 'utc_offset_min'].values[0]))
                s = stations.loc[stations['wban'] == w, :]
                icao.append(s['icao'].values[0])
                station.append(s['station'].values[0])
                state.append(s['state'].values[0])
                country.append(s['country'].values[0])
                lat.append(s['lat'].values[0])
                lon.append(s['lon'].values[0])
                elev_meters.append(s['elev_meters'].values[0])

            new_df['icao'] = icao
            new_df['station'] = station
            new_df['country'] = country
            new_df['state'] = state
            new_df['lat'] = lat
            new_df['lon'] = lon
            new_df['elev_meters'] = elev_meters
            new_df['date_time_utc'] = [datetime.strptime(d, '%Y-%m-%dT%H:%M:%S') -
                                       utc_offset[i]
                                       for i, d in enumerate(df['DATE'].values)]
            new_df['report_type'] = df['REPORT_TYPE'].str.strip()
            new_df['source'] = df['SOURCE'].str.strip()
            new_df['hrly_altimeter_setting_inhg'] = df['HourlyAltimeterSetting'].values
            new_df['hrly_dew_point_temp_f'] = df['HourlyDewPointTemperature'].values
            new_df['hrly_dry_bulb_temp_f'] = df['HourlyDryBulbTemperature'].values
            new_df['hrly_wet_bulb_temp_f'] = df['HourlyWetBulbTemperature'].values
            new_df['hrly_precipitation'] = df['HourlyPrecipitation'].values
            new_df['hrly_weather_type'] = df['HourlyPresentWeatherType'].values
            new_df['hrly_press_change'] = df['HourlyPressureChange'].values
            new_df['hrly_press_tendency'] = df['HourlyPressureTendency'].values
            new_df['hrly_relative_humidity'] = df['HourlyRelativeHumidity'].values
            new_df['hrly_sea_level_press_inhg'] = df['HourlySeaLevelPressure'].values
            new_df['hrly_sky_conditions'] = df['HourlySkyConditions'].values
            new_df['hrly_station_press_inhg'] = df['HourlyStationPressure'].values
            new_df['hrly_visibility'] = df['HourlyVisibility'].values
            new_df['hrly_wind_direction'] = df['HourlyWindDirection'].values
            new_df['hrly_wind_speed_mph'] = df['HourlyWindSpeed'].values
            new_df['hrly_rem'] = df['REM'].values

            # Sunrise (need conversion or some formatting)
            # Sunset (need conversion or some formatting)

            new_df.loc[new_df['hrly_precipitation'] == 'T', 'hrly_precipitation'] = 0
            ignore_types = ['SOD', 'SOM']
            new_df.drop(new_df[new_df['report_type'].isin(ignore_types)].index,
                        inplace=True)

            print('  Sorting records of processed file')
            new_df.sort_values(by=['date_time_utc', 'wban'],
                               ascending=True, inplace=True)
            print('  Saving file', proc_file)
            new_df.to_csv(proc_file, index=False)

print('\nDone!')
