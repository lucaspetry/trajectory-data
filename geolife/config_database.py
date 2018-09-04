from core.logger import Logger
from core.database import Database
import argparse
import configparser
import os
import pandas as pd


logger = Logger()
arg_parser = argparse.ArgumentParser(
    description='Create/import the geolife dataset.')
arg_parser.add_argument('operation',
                        choices=['create', 'drop'],
                        help='The operation to be done.',
                        type=str)
arg_parser.add_argument('folder',
                        help='The dataset folder.',
                        type=str)
arg_parser.add_argument('config',
                        help='Configuration file.',
                        type=str)
args = arg_parser.parse_args()

CREATE_SCHEMA_FILE = 'sql/create_schema.sql'
DROP_SCHEMA_FILE = 'sql/drop_schema.sql'
CONFIG_FILE = args.config

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

db = Database()
db.config(config['DATABASE']['NAME'],
          config['DATABASE']['HOST'],
          config['DATABASE']['USER'],
          config['DATABASE']['PASS'])

if(db.connect()):
    logger.log(Logger.INFO, "Succesfully connected to database \'" +
               str(config['DATABASE']['NAME']) + "\'!")
else:
    logger.log(Logger.ERROR, "Failed connecting to database \'" +
               str(config['DATABASE']['NAME']) + "\'!")

if args.operation == 'create':
    logger.log(Logger.INFO, "Creating schema for database '" +
               str(config['DATABASE']['NAME']) + "'... ")
    db.execute(open(CREATE_SCHEMA_FILE, "r").read())
    logger.log(Logger.INFO, "Creating schema for database '" +
               str(config['DATABASE']['NAME']) + "'... SUCCESS!")

    logger.log(Logger.INFO, "Importing data... ")
    users = sorted(os.listdir(args.folder))
    count = 0
    transp = {'walk': '1',
              'bike': '2',
              'bus': '3',
              'car': '4',
              'taxi': '5',
              'subway': '6',
              'train': '7',
              'airplane': '8',
              'boat': '9',
              'run': '10',
              'motorcycle': '11'}

    for key in transp:
        db.execute("INSERT INTO ge_transportation(id, mode) VALUES (" +
                   transp[key] + ", '" + key + "')")

    db.commit()

    for user in users:
        root = args.folder + '/' + user + '/Trajectory/'
        points = sorted(os.listdir(root))
        modes = args.folder + '/' + user + '/labels.txt'
        db.execute('INSERT INTO ge_user(id) VALUES (' + user + ')')

        for point_file in points:
            with open(root + point_file) as f:
                for _ in range(6):
                    next(f)  # Skip first 6 lines of every file

                for line in f:
                    lat, lon, _, altitude, _, date, time = line.split(',')
                    date_time = date + ' ' + time
                    point_query = """INSERT INTO ge_point(user_id, geom, altitude,
                                     date_time, utc_offset) VALUES (""" + user + \
                        """, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), :altitude,
                           ':date_time', 8)"""

                    point_query = point_query.replace(':lat', lat)
                    point_query = point_query.replace(':lon', lon)
                    point_query = point_query.replace(':date_time', date_time)
                    point_query = point_query.replace(':altitude', altitude)

                    db.execute(point_query)
                    count += 1
                    logger.log_dyn(Logger.INFO, 'Inserting user ' + user +
                                   ' (' + str(count) + ' points imported).')

        if os.path.isfile(modes):
            df = pd.read_csv(modes, sep='\t')
            for index, row in df.iterrows():
                start, end, mode = (row['Start Time'], row['End Time'],
                                    row['Transportation Mode'])
                update_query = "UPDATE ge_point SET transportation_id = " + \
                               ":mode WHERE user_id = :user AND " + \
                               "date_time >= ':start' AND date_time <= ':end'"
                update_query = update_query.replace(":mode", transp[mode])
                update_query = update_query.replace(":user", user)
                update_query = update_query.replace(":start", start)
                update_query = update_query.replace(":end", end)
                db.execute(update_query)

        db.commit()

    logger.log(Logger.INFO, "Importing data... SUCCESS!")
    db.close()
    exit()
elif args.operation == 'drop':
    option = logger.get_answer("The drop option will clear the database and " +
                               "drop all existing tables. Do you want to " +
                               "continue? (y/N) ").lower()

    if option != 'y':
        exit()

    logger.log_dyn(Logger.INFO, "Dropping schema for database '" +
                   str(config['DATABASE']['NAME']) + "'... ")
    db.execute(open(DROP_SCHEMA_FILE, "r").read())
    db.commit()
    logger.log(Logger.INFO, "Dropping schema for database '" +
               str(config['DATABASE']['NAME']) + "'... SUCCESS!")
    db.close()
    exit()
