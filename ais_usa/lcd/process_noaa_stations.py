import os
import pandas as pd
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime


tf = TimezoneFinder()
station_file = 'noaa_station_usa_west_coast.csv'
updated_station_file = 'noaa_station_usa_west_coast_order_list.csv'
out_file = 'processed/lcd_station_usa_west_coast.csv'

if not os.path.isdir('processed'):
    os.mkdir('processed')

df = pd.read_csv(station_file)
df_updated = pd.read_csv(updated_station_file)

df_updated['usaf'] = [None for i in range(0, len(df_updated))]
df_updated['alternative_name'] = [None for i in range(0, len(df_updated))]
df_updated['lat'] = [None for i in range(0, len(df_updated))]
df_updated['lon'] = [None for i in range(0, len(df_updated))]
df_updated['elev_meters'] = [None for i in range(0, len(df_updated))]
df_updated['icao'] = [None for i in range(0, len(df_updated))]
df_updated['record_begin'] = [None for i in range(0, len(df_updated))]
df_updated['record_end'] = [None for i in range(0, len(df_updated))]

for i, row in df_updated.iterrows():
    old_row = df.loc[df['WBAN'] == row['wban'], :].values[0]
    beg = str(old_row[9])
    end = str(old_row[10])
    beg = beg[:4] + '-' + beg[4:6] + '-' + beg[-2:]
    end = end[:4] + '-' + end[4:6] + '-' + end[-2:]

    df_updated.loc[i, 'usaf'] = old_row[0]
    df_updated.loc[i, 'alternative_name'] = old_row[2]
    df_updated.loc[i, 'lat'] = old_row[6]
    df_updated.loc[i, 'lon'] = old_row[7]
    df_updated.loc[i, 'elev_meters'] = old_row[8]
    df_updated.loc[i, 'icao'] = old_row[5]
    df_updated.loc[i, 'record_begin'] = beg
    df_updated.loc[i, 'record_end'] = end
    tz_target = pytz.timezone(tf.certain_timezone_at(lng=old_row[7],
                                                     lat=old_row[6]))
    x = datetime(2000, 1, 1, 0, 0, 0)
    diff = pytz.utc.localize(x) - \
        tz_target.localize(x)
    df_updated.loc[i, 'utc_offset_min'] = int(diff.total_seconds() / 60)

df_updated.to_csv(out_file, index=False)
