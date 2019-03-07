import os
import glob
import pandas as pd


file_pattern = ':dir/*:year.csv'
proc_dir = 'processed/'
years = ['2015']


if not os.path.isdir(proc_dir):
    os.mkdir(proc_dir)

for year in years:
    pattern = file_pattern.replace(':dir', '.') \
                          .replace(':year', year)
    files = glob.glob(pattern)

    for file in files:
        print('Processing file', file)
        proc_file = file.replace('./', proc_dir)
        df = pd.read_csv(file)

        # TO-DO

print('\nDone!')
