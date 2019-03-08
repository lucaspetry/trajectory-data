from os import path
import os
from datetime import datetime
import pandas as pd


proc_dir = 'processed'
file = ':dir/:year/AIS_:year_:month_Zone:zone.csv'
file_out = ':dir/:year/AIS_:year_:month.csv'
vessel_file = 'vessel_types.csv'
years = ['2015']
months = ['01', '02', '03', '04', '05', '06',
          '07', '08', '09', '10', '11', '12']

# Zones go from 01 to 20 (zones 12 and 13 do not exist)
# Currently retrieving only the zones corresponding to the USA west coast
zones = ['06', '07', '08', '09', '10', '11']

vessels = pd.read_csv(vessel_file)


def get_vessel_group(ntype):
    return vessels.loc[vessels['type_number'] == ntype,
                       'type_group'].values[0]


def get_vessel_desc(ntype):
    return vessels.loc[vessels['type_number'] == ntype,
                       'description'].values[0]


if not path.isdir(proc_dir):
    os.mkdir(proc_dir)

for year in years:
    if not path.isdir(path.join(proc_dir, year)):
        os.mkdir(path.join(proc_dir, year))

    for month in months:
        print('Processing AIS for', month, '/', year)
        to_save = file_out.replace(':dir', proc_dir) \
                          .replace(':year', year) \
                          .replace(':month', month)
        data = None

        for zone in zones:
            print('  Processing AIS for Zone', zone)
            to_process = file.replace(':dir', 'AIS_ASCII_by_UTM_Month') \
                             .replace(':year', year) \
                             .replace(':month', month) \
                             .replace(':zone', zone)

            if not path.isfile(to_process):
                print('  File', to_process, 'not found!')
                continue

            df = pd.read_csv(to_process)
            new_df = pd.DataFrame()
            v_type = [0 if pd.isna(t) else int(t)
                      for t in df['VesselType']]
            new_df['MMSI'] = df['MMSI']
            new_df['IMO'] = [0 if i == '' else str(i)[3:] for i in df['IMO']]
            new_df['DateTime'] = \
                [datetime.strptime(d, '%Y-%m-%dT%H:%M:%S')
                 for d in df['BaseDateTime'].values]
            new_df['Lat'] = df['LAT']
            new_df['Lon'] = df['LON']
            new_df['SOG'] = df['SOG']
            new_df['COG'] = df['COG']
            new_df['Heading'] = df['Heading']
            new_df['VesselName'] = df['VesselName']
            new_df['CallSign'] = df['CallSign']
            new_df['VesselType'] = v_type
            new_df['VesselTypeGroup'] = \
                [get_vessel_group(v) for v in v_type]
            new_df['VesselTypeDescription'] = \
                [get_vessel_desc(v) for v in v_type]
            new_df['Status'] = df['Status']
            new_df['Length'] = df['Length']
            new_df['Width'] = df['Width']
            new_df['Draft'] = df['Draft']
            new_df['Cargo'] = df['Cargo']
            new_df['Zone'] = zone

            if data is not None:
                data = pd.concat([data, new_df], ignore_index=True)
            else:
                data = new_df

        print('  Sorting records of processed file(s)')
        data.sort_values(by=['DateTime', 'IMO'], ascending=True, inplace=True)
        data['IMO'] = data['IMO'].astype('int')
        data['VesselType'] = data['VesselType'].astype('int')

        print('  Saving file', to_save)
        data.to_csv(to_save, index=False)

print('\nDone!')
