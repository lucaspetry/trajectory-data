from core.logger import Logger
from db_spec import DBSPEC
from datetime import datetime
import pytz
from tzwhere import tzwhere
import csv

logger = Logger()
DB = None
GEO = tzwhere.tzwhere(forceTZ=True)


def parse_date_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')


def offset_from_utc_offset_str(utc_offset):
    signal = 1 if utc_offset[0] == '+' else -1
    hour = int(utc_offset[1:3])
    minute = int(utc_offset[3:5])
    return signal * hour * 60 + signal * minute


def import_checkins(checkin_file):
    checkin_count = DB.query("SELECT COUNT(*) FROM " + DBSPEC.TB_CHECKIN + ";")[0][0]

    if checkin_count > 0:
        logger.log(Logger.INFO, "Check-in table already populated! " + str(checkin_count) + " check-ins were found.")
        return

    count = 0
    user_count = 0

    logger.log(Logger.INFO, "Restarting check-in table sequence... ")
    DB.execute("ALTER SEQUENCE " + DBSPEC.TB_CHECKIN + "_id_seq RESTART WITH 1")
    DB.commit()
    logger.log(Logger.INFO, "Restarting check-in table sequence... SUCCESS!")

    with open(checkin_file, 'r') as checkins:
        reader = csv.reader(checkins, delimiter='\t')

        for user, date_time, lat, lon, location_id in reader:
            if user == '' or lat == '' or lon == '' or date_time == '' \
               or float(lat) == 0 or float(lon) == 0 \
               or location_id == '00000000000000000000000000000000':
                continue

            # Inserts the user if doesn't exist
            user_in_db = DB.query("SELECT COUNT(*) FROM " + DBSPEC.TB_USER + " WHERE id = " + str(user) + ";")[0][0]

            if user_in_db == 0:
                DB.execute("INSERT INTO " + DBSPEC.TB_USER + " (id) VALUES (" + str(user) + ");")
                user_count += 1

            # Inserts the check-in
            insert_query = "INSERT INTO " + DBSPEC.TB_CHECKIN + """ (user_id,
                geom, location_id, date_time, utc_offset) VALUES
                (:user_id, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                 :location_id, :date_time, :utc_offset);"""

            try:
                date_time = parse_date_time(date_time)
                timezone = GEO.tzNameAt(float(lat), float(lon), forceTZ=True)

                if not timezone:
                    logger.log(Logger.ERROR, "No timezone info found for location " +
                               str(lat) + ", " + str(lon) + "!")

                utc_offset = pytz.timezone(timezone).localize(date_time).strftime('%z')
                offset = offset_from_utc_offset_str(utc_offset)

                insert_query = insert_query.replace(":user_id", str(user))
                insert_query = insert_query.replace(":lat", str(lat))
                insert_query = insert_query.replace(":lon", str(lon))
                insert_query = insert_query.replace(":location_id", "'" + str(location_id) + "'")
                insert_query = insert_query.replace(":date_time", "'" + str(date_time) + "'")
                insert_query = insert_query.replace(":utc_offset", str(offset))
                DB.execute(insert_query)

                count += 1
                logger.log_dyn(Logger.INFO, str(count) + " check-ins imported! Current: location " + str(location_id) + " from user " + str(user) + ".")
            except Exception as e:
                logger.log(Logger.ERROR, str(e))
                logger.log(Logger.ERROR, "Entry (" + str(user) + ", " + str(lat) + ", " + str(lon) + ", " +
                           str(location_id) + ", " + str(date_time) + ") could not be processed!")

    DB.commit()
    logger.log(Logger.INFO, str(user_count) + " users imported!")
    logger.log(Logger.INFO, str(count) + " check-ins imported!")

    return True


def update_checkins_count():
    logger.log(Logger.INFO, "Updating users check-ins count... ")
    users = DB.query("""SELECT user_id, COUNT(*) FROM """ + DBSPEC.TB_CHECKIN + """
        GROUP BY user_id
        ORDER BY user_id ASC""")

    for row in users:
        update_query = "UPDATE " + DBSPEC.TB_USER + """ SET checkin_count = :count WHERE id = :id"""
        update_query = update_query.replace(":id", str(row[0]))
        update_query = update_query.replace(":count", str(row[1]))
        DB.execute(update_query)
        logger.log_dyn(Logger.INFO, "User " + str(row[0]) + " updated!")

    DB.commit()
    logger.log(Logger.INFO, "Updating users check-ins count... SUCCESS!")


def import_friends(friends_file):
    friends_count = DB.query("SELECT COUNT(*) FROM " + DBSPEC.TB_FRIENDSHIP + ";")[0][0]

    if friends_count > 0:
        logger.log(Logger.INFO, "Friendship table already populated! " + str(friends_count) + " friendships were found.")
        return

    count = 0

    with open(friends_file, 'r') as friends:
        reader = csv.reader(friends, delimiter='\t')

        for user_id, friend_id in reader:
            # Inserts the user if doesn't exist
            user_in_db = DB.query("SELECT COUNT(*) FROM " + DBSPEC.TB_USER + " WHERE id = " + str(user_id) + ";")[0][0]

            if user_in_db == 0:
                DB.execute("INSERT INTO " + DBSPEC.TB_USER + " (id) VALUES (" + str(user_id) + ");")

            # Inserts the friend if doesn't exist
            friend_in_db = DB.query("SELECT COUNT(*) FROM " + DBSPEC.TB_USER + " WHERE id = " + str(friend_id) + ";")[0][0]

            if friend_in_db == 0:
                DB.execute("INSERT INTO " + DBSPEC.TB_USER + " (id) VALUES (" + str(friend_id) + ");")

            # Inserts the friendship
            insert_query = "INSERT INTO " + DBSPEC.TB_FRIENDSHIP + """ (user_id, friend_id) VALUES
                (:user_id, :friend_id);"""

            try:
                insert_query = insert_query.replace(":user_id", str(user_id))
                insert_query = insert_query.replace(":friend_id", str(friend_id))
                DB.execute(insert_query)

                count += 1
                logger.log_dyn(Logger.INFO, str(count) + " friendships imported! Current: (" + str(user_id) + ", " + str(friend_id) + ").")
            except Exception as e:
                logger.log(Logger.ERROR, str(e))
                logger.log(Logger.ERROR, "Entry (" + str(user_id) + ", " + str(friend_id) + ") could not be processed!")

    DB.commit()
    logger.log(Logger.INFO, str(count) + " friendships imported!")


def update_friends_count():
    logger.log(Logger.INFO, "Updating users friends count... ")
    users = DB.query("""SELECT user_id, COUNT(*) FROM """ + DBSPEC.TB_FRIENDSHIP + """
        GROUP BY user_id
        ORDER BY user_id ASC""")

    for row in users:
        update_query = "UPDATE " + DBSPEC.TB_USER + """ SET friend_count = :count WHERE id = :id"""
        update_query = update_query.replace(":id", str(row[0]))
        update_query = update_query.replace(":count", str(row[1]))
        DB.execute(update_query)
        logger.log_dyn(Logger.INFO, "User " + str(row[0]) + " updated!")

    DB.commit()
    logger.log(Logger.INFO, "Updating users friends count... SUCCESS!")


def import_data(db, config, params):
    global DB

    DB = db
    import_checkins(params[0])
    update_checkins_count()
    import_friends(params[1])
    update_friends_count()
    DB.close()
