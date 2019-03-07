import requests
from os import path
import os
import sys
import zipfile


# For data info go to https://marinecadastre.gov/ais/
url = 'https://coast.noaa.gov/htdata/CMSP/AISDataHandler/:year/AIS_:year_' + \
      ':month_Zone:zone.zip'

file = ':dir/AIS_:year_:month_Zone:zone.:ext'
years = ['2015']
months = ['01', '02', '03', '04', '05', '06',
          '07', '08', '09', '10', '11', '12']

# Zones go from 01 to 20 (zones 12 and 13 do not exist)
# Currently retrieving only the zones corresponding to the USA west coast
zones = ['06', '07', '08', '09', '10', '11']

download_block = 1024 * 1024 * 5
success_count = 0
skip_count = 0
fail_count = 0


def print_downloading(bytes):
    mb = int(bytes / 1024 / 1024)
    msg = '  ' + str(mb) + ' MB downloaded... '
    sys.stdout.write("\r\x1b[K" + msg.__str__())
    sys.stdout.flush()


for year in years:
    for month in months:
        for zone in zones:
            print('Retrieving AIS for Zone', zone, 'of', month, '/', year)
            to_download = url.replace(':year', year) \
                             .replace(':month', month) \
                             .replace(':zone', zone)
            to_save = file.replace(':dir', '.') \
                          .replace(':year', year) \
                          .replace(':month', month) \
                          .replace(':zone', zone) \
                          .replace(':ext', 'zip')
            to_check = file.replace(':dir', path.join('AIS_ASCII_by_UTM_Month',
                                                      ':year')) \
                           .replace(':year', year) \
                           .replace(':month', month) \
                           .replace(':zone', zone) \
                           .replace(':ext', 'csv')

            if path.isfile(to_check):
                print('  File', to_save, 'already processed. Skipping...')
                skip_count += 1
                continue

            try:
                r = requests.get(to_download, stream=True)

                if r.status_code != 200:
                    fail_count += 1
                    print('  Failed to download', to_download)
                    print('  Status code:', r.status_code)
                    continue

                length = int(r.headers['content-length']) / 1024 / 1024
                print('  Content length: %.2f MB' % length)
                with open(to_save, 'wb') as f:
                    size = 0
                    for block in r.iter_content(download_block):
                        f.write(block)
                        size += download_block
                        print_downloading(size)

                print('\n  Extracting ZIP file', to_save)
                to_extract = zipfile.ZipFile(to_save, 'r')
                to_extract.extractall()
                to_extract.close()
                print('  Deleting ZIP file', to_save)
                os.remove(to_save)
                success_count += 1
            except Exception as e:
                fail_count += 1
                print('  Error:', str(e))

                if path.isfile(to_save):
                    os.remove(to_save)

print('\nDownload summary:')
print('  Success:', success_count)
print('  Failed:', fail_count)
print('  Skipped:', skip_count)
