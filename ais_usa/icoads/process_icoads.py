import os
import glob
import pandas as pd
from datetime import datetime
import numpy as np


file_pattern = ':dir/*:year.csv'
proc_dir = 'processed/'
years = ['2015']


def get_prefix(m):
    s1 = min(m)
    s2 = max(m)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1


if not os.path.isdir(proc_dir):
    os.mkdir(proc_dir)

for year in years:
    print('Processing year', year)
    pattern = file_pattern.replace(':dir', '.') \
                          .replace(':year', year)
    files = glob.glob(pattern)
    data = None
    proc_file = proc_dir + get_prefix(files)[2:] + '_:year.csv' \
        .replace(':year', year)

    if os.path.isfile(proc_file):
        os.remove(proc_file)

    for file in files:
        print('  Processing file', file)
        df = pd.read_csv(file)
        df.replace(' ', np.NaN, inplace=True)

        new_df = pd.DataFrame()
        new_df['id'] = df['Identification'].str.strip()
        new_df['lat'] = df['Latitude']
        new_df['lon'] = [l if l <= 180 else l - 360
                         for l in df['Longitude'].values]
        new_df['date_time_utc'] = [datetime.strptime(d, '%Y-%m-%dT%H:%M:%S')
                                   for d in df['Time of Observation'].values]
        new_df['ice_accretion_on_ship'] = df['Ice Accretion On Ship']
        new_df['thickness_ice_accretion_on_ship'] = \
            df['Thickness of Ice Accretion On Ship']
        new_df['rate_ice_accretion_on_ship'] = \
            df['Rate of Ice Accretion on Ship']
        new_df['sea_level_pressure_hpa'] = df['Sea Level Pressure']
        new_df['characteristics_press_tendency'] = \
            df['Characteristics of Pressure Tendency']
        new_df['press_tendency'] = df['Pressure Tendency']
        new_df['air_temp_c'] = df['Air Temperature']
        new_df['wet_bulb_temp_c'] = df['Wet Bulb Temperature']
        new_df['dew_point_temp_c'] = df['Dew Point Temperature']
        new_df['sea_surface_temp_c'] = df['Sea Surface Temperature']
        new_df['wave_direction'] = df['Wave Direction']
        new_df['wave_period'] = df['Wave Period']
        new_df['wave_height_meters'] = df['Wave Height'].astype(float) / 2
        new_df['swell_direction'] = df['Swell Direction']
        new_df['swell_period'] = df['Swell Period']
        new_df['swell_height_meters'] = df['Swell Height'].astype(float) / 2
        new_df['total_cloud_amount'] = df['Total Cloud Amount']
        new_df['low_cloud_amount'] = df['Low Cloud Amount']
        new_df['low_cloud_type'] = df['Low Cloud Type']
        new_df['cloud_height_indic'] = df['Cloud Height Indicator']
        new_df['cloud_height'] = df['Cloud Height']
        new_df['middle_cloud_type'] = df['Middle Cloud Type']
        new_df['high_cloud_type'] = df['High Cloud Type']
        new_df['visibility'] = df['Visibility']
        new_df['visibility_indic'] = df['Visibility Indicator']
        new_df['present_weather'] = df['Present Weather']
        new_df['past_weather'] = df['Past Weather']
        new_df['wind_direction'] = df['Wind Direction']
        new_df['wind_speed_ms'] = df['Wind Speed']

        if data is not None:
            data = pd.concat([data, new_df], ignore_index=True)
        else:
            data = new_df

    print('  Sorting records of processed file(s)')
    data.sort_values(by=['date_time_utc', 'id'],
                     ascending=True, inplace=True)
    print('  Saving file', proc_file)
    data.to_csv(proc_file, index=False)

print('\nDone!')
