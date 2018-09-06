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
                        choices=['create', 'drop', 'segment'],
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
    tid = 1

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
                    point_query = """INSERT INTO ge_point(tid, user_id, geom, altitude,
                                     date_time, utc_offset) VALUES (""" + str(tid) + ", " + user + \
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
            tid += 1

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
elif args.operation == 'segment':
    tidcol_query = "ALTER TABLE ge_point ADD COLUMN mode_tid INTEGER"
    users_query = "SELECT DISTINCT user_id FROM ge_point ORDER BY user_id ASC"
    select_query = """SELECT p.id, p.tid, t.mode FROM ge_point p
                      INNER JOIN ge_transportation t ON p.transportation_id =
                      t.id
                      WHERE p.user_id = :user
                      ORDER BY p.tid ASC, date_time ASC"""
    update_query = "UPDATE ge_point SET mode_tid" + \
                   " = :tid WHERE id IN (:point_ids)"
    traj_id = 1

    logger.log(Logger.INFO, "Segmenting trajectories... ")
    db.execute(tidcol_query)
    
    for user in db.query(users_query):
        points = db.query(select_query.replace(":user", str(user[0])))
        update_ids = []
        cur_mode = None

        for id, tid, mode in points:
            if mode != cur_mode and len(update_ids) > 0:
                db.execute(
                    update_query.replace(":tid", str(traj_id))
                    .replace(":point_ids", str(update_ids)[1:-1]))
                update_ids = []
                traj_id += 1

            cur_mode = mode
            update_ids.append(id)

        if len(update_ids) > 0:
            db.execute(
                update_query.replace(":tid", str(traj_id))
                .replace(":point_ids", str(update_ids)[1:-1]))
            update_ids = []
            traj_id += 1

        db.commit()
        logger.log_dyn(Logger.INFO, "User " + str(user[0]) + " segmented (" +
                       str(traj_id - 1) + " segments created).")

    db.close()
    logger.log(Logger.INFO, "Segmenting trajectories... SUCCESS!")
