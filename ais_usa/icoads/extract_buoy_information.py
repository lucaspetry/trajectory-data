import os
import glob
import pandas as pd


file_pattern = ':dir/*:year.csv'
proc_dir = 'processed'
buoys_file = os.path.join(proc_dir, 'icoads_buoys_ships.csv')
years = ['2015']

data = None

if not os.path.isdir(proc_dir):
    os.mkdir(proc_dir)

for year in years:
    print('Processing year', year)
    pattern = file_pattern.replace(':dir', '.') \
                          .replace(':year', year)
    files = glob.glob(pattern)

    for file in files:
        print('  Processing file', file)
        df = pd.read_csv(file).loc[:, ['Identification',
                                       'Latitude', 'Longitude']]
        df['Longitude'] = [l if l <= 180 else l - 360
                           for l in df['Longitude'].values]
        df.drop_duplicates(inplace=True)
        print('   ', len(df), 'buoys/ships found in file!')

        if data is not None:
            data = pd.concat([data, df], ignore_index=True)
        else:
            data = df

data.columns = ['id', 'lat', 'lon']
data['id'] = data['id'].str.strip()
data.drop_duplicates('id', inplace=True)

print('Sorting records of processed file(s)')
data.sort_values(by=['id'], ascending=True, inplace=True)

print('Saving file', buoys_file)
data.to_csv(buoys_file, index=False)

print('\nDone!')
