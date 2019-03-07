import glob
import os
import pandas as pd


file_pattern = ':dir/*:year_:month.csv'
proc_dir = 'processed/'
years = ['2015']
months = ['01', '02', '03', '04', '05', '06',
          '07', '08', '09', '10', '11', '12']


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

            # TO-DO

            df.to_csv(proc_file, index=False)

print('\nDone!')
