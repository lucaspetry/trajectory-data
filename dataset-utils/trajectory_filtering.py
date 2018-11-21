from core.logger import Logger
from core.database import Database
import argparse


logger = Logger()
db = Database()
arg_parser = argparse.ArgumentParser(description='Segment trajectories.')
arg_parser.add_argument('dbname',
                        help='The database name.',
                        type=str)
arg_parser.add_argument('origtable',
                        help='The database trajectory table.',
                        type=str)
arg_parser.add_argument('totable',
                        help='The database trajectory table to be created with the filtered trajectories.',
                        type=str)
arg_parser.add_argument('tidcol',
                        help='The name of the column to be created in the ' +
                        'database table for holding the new trajectory IDs.',
                        type=str)
arg_parser.add_argument('classcol',
                        help='The name of the class column of trajectories.',
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
arg_parser.add_argument('--filter-category',
                        help='Whether or not to filter categories (no category and broad categories).',
                        action='store_true')
arg_parser.add_argument('--filter-duplicates',
                        default=-1,
                        help='The interval in minutes to remove duplicate check-ins (-1 means no removal) (default: -1).',
                        type=int)
arg_parser.add_argument('--min-traj-length',
                        default=1,
                        help='The minimum length of trajectories (default: 1).',
                        type=int)
arg_parser.add_argument('--min-traj-count',
                        default=1,
                        help='The minimum number of trajectories per class (default: 1).',
                        type=int)
arg_parser.add_argument('--userfilter',
                        help='A filter on the selected users (in the format of a SQL WHERE expression).',
                        type=str)
#arg_parser.add_argument('--plot', action='store_true', help='Pass.')
args = arg_parser.parse_args()

db.config(name=args.dbname,
          host=args.dbhost,
          user=args.dbuser,
          passwd=args.dbpass)


def close_db_terminate():
    global db
    db.rollback()
    db.close()
    exit()


def print_table_stats(table, tidcol, classcol):
    global db, logger

    checkin_count =  db.query("SELECT COUNT(*) FROM " + table)[0][0]
    traj_count = db.query("SELECT COUNT(DISTINCT(" + tidcol + ")) FROM " +
                          table)[0][0]
    class_count = db.query("SELECT COUNT(DISTINCT(" + classcol + ")) FROM " +
                           table)[0][0]

    logger.log(Logger.INFO, "Table " + table + " Stats: ")
    logger.log(Logger.INFO, "      Check-in count:   " + str(checkin_count))
    logger.log(Logger.INFO, "      Trajectory count: " + str(traj_count))
    logger.log(Logger.INFO, "      Class count:      " + str(class_count))


if(db.connect()):
    logger.log(Logger.INFO, "Succesfully connected to database \'" +
               args.dbname + "\'!")
else:
    logger.log(Logger.ERROR, "Failed connecting to database \'" +
               args.dbname + "\'!")
    logger.log(Logger.ERROR, "Database status: " + db.status())
    exit()

insert_table_query = "CREATE TABLE " + args.totable + \
                     " AS (SELECT * FROM " + args.origtable + " WHERE " + \
                     args.tidcol + " IS NOT NULL :where)"

no_cat_query = """DELETE FROM :table WHERE venue_id IN (
    SELECT venue_id FROM :table
    EXCEPT
    SELECT v.id FROM fq_venue v
    INNER JOIN fq_venue_category vc ON v.id = vc.venue_id
)"""

broad_cat_query = """DELETE FROM :table WHERE venue_id IN (
    SELECT v.id FROM fq_venue v
        INNER JOIN fq_venue_category vc ON v.id = vc.venue_id
        INNER JOIN fq_category c ON vc.category_id = c.id
        WHERE c.foursquare_id IN (
            '56aa371be4b08b9a8d573544', -- Bay
            '56aa371be4b08b9a8d573562', -- Canal
            '4bf58dd8d48988d162941735', -- Other Great Outdoors
            '4eb1d4dd4b900d56c88a45fd', -- River
            '530e33ccbcbc57f1066bbfe4', -- States & Municipalities
            '50aa9e094b90af0d42d5de0d', -- City
            '5345731ebcbc57f1066c39b2', -- County
            '530e33ccbcbc57f1066bbff7', -- Country
            '4f2a25ac4b909258e854f55f', -- Neighborhood
            '530e33ccbcbc57f1066bbff8', -- State
            '530e33ccbcbc57f1066bbff3', -- Town
            '530e33ccbcbc57f1066bbff9', -- Village
            '4bf58dd8d48988d12d951735', -- Boat or Ferry
            '4bf58dd8d48988d1f6931735', -- General Travel
            '52f2ab2ebcbc57f1066b8b4c', -- Intersection
            '4f2a23984b9023bd5841ed2c', -- Moving Target
            '4bf58dd8d48988d1f9931735', -- Road
            '4bf58dd8d48988d130951735', -- Taxi
            '4bf58dd8d48988d129951735'  -- Train Station
        )
)"""

remove_duplicate_query = """DELETE FROM :table WHERE id IN
(
    SELECT DISTINCT(t1.id) FROM :table t1
    INNER JOIN :table t2 ON t1.id < t2.id
        AND t1.anonymized_user_id = t2.anonymized_user_id
        AND t1.venue_id = t2.venue_id
        AND "timestamp"(t1.date_time) - "timestamp"(t2.date_time) <= (interval '1 minute' * :duplicate_interval)
        AND "timestamp"(t1.date_time) - "timestamp"(t2.date_time) >= (interval '-1 minute' * :duplicate_interval)
    ORDER BY t1.id
)"""

traj_remove_query = """DELETE FROM :table WHERE :tid IN (
    SELECT :tid FROM :table
    GROUP BY :tid HAVING COUNT(*) < :min_length
    ORDER BY :tid
)"""

class_query = """SELECT :class, :tid, COUNT(*) as count FROM :table
                 GROUP BY :class, :tid
                 ORDER BY :class ASC, :tid ASC"""

remove_class_query = "DELETE FROM :table WHERE :class IN (:values)"

try:
    logger.log(Logger.INFO, "Creating new table '" + args.totable + "'... ")

    if args.userfilter:
        insert_table_query = insert_table_query.replace(":where", "AND " + args.userfilter)
    else:
        insert_table_query = insert_table_query.replace(":where", "")

    db.execute(insert_table_query)
    db.commit()
    print_table_stats(table=args.totable,
                      tidcol=args.tidcol,
                      classcol=args.classcol)
    logger.log(Logger.INFO, "Creating new table '" + args.totable + "'... DONE!")
except Exception as e:
    logger.log(Logger.ERROR, str(e))
    close_db_terminate()

# Filter categories
if args.filter_category:
    logger.log(Logger.INFO, "Filtering categories... ")
    no_cat_query = no_cat_query.replace(":table", args.totable)
    broad_cat_query = broad_cat_query.replace(":table", args.totable)

    try:
        db.execute(no_cat_query)
        db.execute(broad_cat_query)
        db.commit()

        print_table_stats(table=args.totable,
                          tidcol=args.tidcol,
                          classcol=args.classcol)
        logger.log(Logger.INFO, "Filtering categories... DONE!")
    except Exception as e:
        logger.log(Logger.ERROR, str(e))
        close_db_terminate()


# Filter duplicates
if args.filter_duplicates != -1:
    threshold = args.filter_duplicates
    logger.log(Logger.INFO, "Filtering duplicates with a " +
                            str(threshold) + "-minute threshold...")

    remove_duplicate_query = remove_duplicate_query\
        .replace(":table", args.totable)\
        .replace(":duplicate_interval", str(threshold))
    db.execute(remove_duplicate_query)
    db.commit()

    print_table_stats(table=args.totable,
                      tidcol=args.tidcol,
                      classcol=args.classcol)
    logger.log(Logger.INFO, "Filtering duplicates with a " +
                            str(threshold) + "-minute threshold... DONE!")

# Filter trajectories by length
logger.log(Logger.INFO, "Filtering trajectories with length smaller than " + 
                        str(args.min_traj_length) + "... ")
traj_remove_query = traj_remove_query.replace(":tid", args.tidcol)
traj_remove_query = traj_remove_query.replace(":table", args.totable)
traj_remove_query = traj_remove_query.replace(":min_length", str(args.min_traj_length))

try:
    db.execute(traj_remove_query)
    db.commit()
    print_table_stats(table=args.totable,
                      tidcol=args.tidcol,
                      classcol=args.classcol)
    logger.log(Logger.INFO, "Filtering trajectories with length smaller than " + 
                            str(args.min_traj_length) + "... DONE!")
except Exception as e:
    logger.log(Logger.ERROR, str(e))
    close_db_terminate()



# Filter classes by trajectory count
logger.log(Logger.INFO, "Filtering classes with fewer than " + 
                        str(args.min_traj_count) + " trajectories ... ")
class_query = class_query.replace(":class", args.classcol)
class_query = class_query.replace(":tid", args.tidcol)
class_query = class_query.replace(":table", args.totable)
cls_to_remove = []

last_cls = None
cls_count = 0

for cls, tid, count in db.query(class_query):
    if last_cls and cls != last_cls:
        if cls_count < args.min_traj_count:
            cls_to_remove.append(last_cls)

        cls_count = 0

    last_cls = cls
    cls_count += 1

if cls_count < args.min_traj_count:
    cls_to_remove.append(last_cls)

try:
    remove_class_query = remove_class_query.replace(":table", args.totable)
    remove_class_query = remove_class_query.replace(":class", args.classcol)
    remove_class_query = remove_class_query.replace(":values", str(cls_to_remove).replace('[', '')
                                                                                 .replace(']', ''))
    db.execute(remove_class_query)
    db.commit()
    print_table_stats(table=args.totable,
                      tidcol=args.tidcol,
                      classcol=args.classcol)
    logger.log(Logger.INFO, "Filtering classes with fewer than " + 
                            str(args.min_traj_count) + " trajectories ... DONE!")
except Exception as e:
    logger.log(Logger.ERROR, str(e))
    close_db_terminate()

db.close()
