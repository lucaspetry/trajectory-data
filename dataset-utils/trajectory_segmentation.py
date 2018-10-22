from core.logger import Logger
from core.database import Database
import argparse


logger = Logger()
db = Database()
arg_parser = argparse.ArgumentParser(description='Segment trajectories.')
arg_parser.add_argument('dbname',
                        help='The database name.',
                        type=str)
arg_parser.add_argument('dbtable',
                        help='The database trajectory table.',
                        type=str)
arg_parser.add_argument('tidcol',
                        help='The name of the column to be created in the ' +
                        'database table for holding the new trajectory IDs.',
                        type=str)
arg_parser.add_argument('--dbhost',
                        default='localhost',
                        help='The database host (default: localhost).',
                        type=str)
arg_parser.add_argument('--dbuser',
                        default='postgres',
                        help='The database username (default: postgres).',
                        type=str)
arg_parser.add_argument('--dbpass',
                        default='postgres',
                        help='The database password (default: postgres).',
                        type=str)
arg_parser.add_argument('--segtype',
                        choices=['daily', 'weekly', 'monthly'],
                        default='weekly',
                        help='How trajectories should be segmented (default: weekly).',
                        type=str)
arg_parser.add_argument('--userfilter',
                        help='A filter on the selected users (in the format of a SQL WHERE expression).',
                        type=str)
#arg_parser.add_argument('--plot', action='store_true', help='Pass.')
args = arg_parser.parse_args()

db.config(name=args.dbname,
          host=args.dbhost,
          user=args.dbuser,
          passwd=args.dbpass)

if(db.connect()):
    logger.log(Logger.INFO, "Succesfully connected to database \'" +
               args.dbname + "\'!")
else:
    logger.log(Logger.ERROR, "Failed connecting to database \'" +
               args.dbname + "\'!")
    logger.log(Logger.ERROR, "Database status: " + db.status())
    exit()

tidcol_query = "ALTER TABLE " + args.dbtable + \
               " ADD COLUMN " + args.tidcol + " INTEGER"

users_query = "SELECT DISTINCT(anonymized_user_id) FROM " + \
              args.dbtable + " :where ORDER BY anonymized_user_id"

checkins_query = "SELECT id, anonymized_user_id, date_time FROM " + \
                 args.dbtable + " WHERE anonymized_user_id = :user_id " + \
                 "ORDER BY date_time ASC"

update_query = "UPDATE " + args.dbtable + " SET " + args.tidcol + \
               " = :tid WHERE id IN (:checkin_ids)"

seg_fun = lambda x : x.isocalendar()[1]

if args.segtype == 'daily':
    seg_fun = lambda x: x.day
elif args.segtype == 'monthly':
    seg_fun = lambda x: x.month

traj_id = 1
user_count = 0
update_interval = 20
update_queries = []

try:
    db.execute(tidcol_query)

    if args.userfilter:
        users_query = users_query.replace(":where", "WHERE " + args.userfilter)
    else:
        users_query = users_query.replace(":where", "")

    users = db.query(users_query)

    for user_id in users:
        checkins = db.query(checkins_query.replace(":user_id", str(user_id[0])))
        update_ids = []
        cur_seg = None

        for checkin_id, user, date in checkins:
            seg = seg_fun(date)

            if seg != cur_seg and len(update_ids) > 0:
                q = update_query.replace(":tid", str(traj_id)).replace(":checkin_ids", str(update_ids)[1:-1])
                update_queries.append(q)
                update_ids = []
                traj_id += 1

            cur_seg = seg
            update_ids.append(checkin_id)

        if len(update_ids) > 0:
            q = update_query.replace(":tid", str(traj_id)).replace(":checkin_ids", str(update_ids)[1:-1])
            update_queries.append(q)
            update_ids = []
            traj_id += 1

        user_count += 1
        logger.log(Logger.INFO, "User " + str(user_id[0]) + " segmented (" +
                   str(traj_id) + " " + args.segtype + " trajectories created).")

        if user_count % update_interval == 0:
            logger.log(Logger.INFO, "Executing update queries...")
            for query in update_queries:
                db.execute(query)

            update_queries = []
            db.commit()
            logger.log(Logger.INFO, "Executing update queries... DONE!")

    logger.log(Logger.INFO, "Executing update queries...")
    for query in update_queries:
        db.execute(query)

    logger.log(Logger.INFO, "Executing update queries... DONE!")
    db.commit()
except Exception as e:
    logger.log(Logger.ERROR, str(e))
    db.rollback()

db.close()
