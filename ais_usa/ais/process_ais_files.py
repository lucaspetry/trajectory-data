from os import path
import os
import csv
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
    return vessels.loc[vessels['type_number'] == ntype, 'type_group'].values[0]


def get_vessel_desc(ntype):
    return vessels.loc[vessels['type_number'] == ntype, 'description'].values[0]


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
        fields = ['MMSI', 'DateTime', 'Lat', 'Lon', 'SOG', 'COG',
                  'Heading', 'VesselName', 'IMO', 'CallSign', 'VesselType',
                  'VesselTypeGroup', 'VesselTypeDescription', 'Status',
                  'Length', 'Width', 'Draft', 'Cargo', 'Zone']

        with open(to_save, 'w') as o:
            writer = csv.DictWriter(o, fields)
            writer.writeheader()

            for zone in zones:
                print('  Processing AIS for Zone', zone)
                to_process = file.replace(':dir', 'AIS_ASCII_by_UTM_Month') \
                                 .replace(':year', year) \
                                 .replace(':month', month) \
                                 .replace(':zone', zone)

                if not path.isfile(to_process):
                    print('  File', to_process, 'not found!')
                    continue

                with open(to_process, 'r') as i:
                    reader = csv.DictReader(i)

                    for row in reader:
                        v_type = 0 if row['VesselType'] == '' \
                            else int(row['VesselType'])
                        writer.writerow({
                            'MMSI': row['MMSI'],
                            'IMO': 0 if row['IMO'] == '' else row['IMO'][3:],
                            'DateTime': datetime.strptime(
                                row['BaseDateTime'], '%Y-%m-%dT%H:%M:%S'),
                            'Lat': row['LAT'],
                            'Lon': row['LON'],
                            'SOG': row['SOG'],
                            'COG': row['COG'],
                            'Heading': row['Heading'],
                            'VesselName': row['VesselName'],
                            'CallSign': row['CallSign'],
                            'VesselType': v_type,
                            'VesselTypeGroup': get_vessel_group(v_type),
                            'VesselTypeDescription': get_vessel_desc(v_type),
                            'Status': row['Status'],
                            'Length': row['Length'],
                            'Width': row['Width'],
                            'Draft': row['Draft'],
                            'Cargo': row['Cargo'],
                            'Zone': zone
                        })

        print('  Sorting records of processed file')
        df = pd.read_csv(to_save)
        df.sort_values(by=['DateTime', 'IMO'], ascending=True, inplace=True)
        df['IMO'] = df['IMO'].astype('int')
        df['VesselType'] = df['VesselType'].astype('int')
        print('  Saving file', to_save)
        df.to_csv(to_save, index=False)

print('\nDone!')
