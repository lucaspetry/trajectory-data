from core.database import Database
from core.logger import Logger
from core.requests import Requests
from db_spec import DBSPEC
from datetime import datetime
import csv

logger = Logger()
requests = Requests()
DB = None
FQ_V = None
FQ_PREMIUM_CALLS = None
FQ_REGULAR_CALLS = None
FQ_VENUE_ENDPOINT = None
FQ_CATEGORY_ENDPOINT = None


def create_category(data, parent, root):
    for cat in data:
        insert_query = "INSERT INTO " + DBSPEC.TB_CATEGORY + """ (parent_category, root_category,
            foursquare_id, name, plural_name, short_name, icon_prefix, icon_suffix) VALUES
            (:parent_category, :root_category, :foursquare_id, :name, :plural_name, :short_name,
            :icon_prefix, :icon_suffix);"""

        insert_query = insert_query.replace(":parent_category", 'NULL' if not parent else str(parent))
        insert_query = insert_query.replace(":root_category", 'NULL' if not root else str(root))
        insert_query = insert_query.replace(":foursquare_id", "'" + cat['id'] + "'")
        insert_query = insert_query.replace(":name", "'" + cat['name'].replace("'", "''") + "'")
        insert_query = insert_query.replace(":plural_name", "'" + cat['pluralName'].replace("'", "''") + "'")
        insert_query = insert_query.replace(":short_name", "'" + cat['shortName'].replace("'", "''") + "'")
        insert_query = insert_query.replace(":icon_prefix", "'" + cat['icon']['prefix'] + "'")
        insert_query = insert_query.replace(":icon_suffix", "'" + cat['icon']['suffix'] + "'")
        DB.execute(insert_query)
        logger.log_dyn(Logger.INFO, "Category '" + cat['id'] + "' inserted!")

        select_query = "SELECT id FROM " + DBSPEC.TB_CATEGORY + " WHERE foursquare_id = ':foursquare_id'"
        select_query = select_query.replace(":foursquare_id", cat['id'])
        catId = DB.query(select_query)[0][0]

        newRoot = root

        if not newRoot:
            newRoot = catId
            DB.execute("UPDATE " + DBSPEC.TB_CATEGORY + " SET root_category = " + str(catId) + " WHERE id = " + str(catId))

        if len(cat['categories']) > 0:
            create_category(cat['categories'], catId, newRoot)

def create_categories():
    cat_count = DB.query("SELECT COUNT(*) FROM " + DBSPEC.TB_CATEGORY + ";")[0][0]
    
    if cat_count > 0:
        logger.log(Logger.INFO, "Category table already populated! " + str(cat_count) + " categories were found.")
        return True

    logger.log_dyn(Logger.INFO, "Sending request for categories... ")
    rsp = requests.get(FQ_CATEGORY_ENDPOINT, named_params = ['v=' + FQ_V])

    if requests.validate(rsp):
        logger.log(Logger.INFO, "Sending request for categories... SUCCESS!")

        logger.log(Logger.INFO, "Creating categories... ")
        create_category(rsp['response']['categories'], None, None)
        DB.commit()
        logger.log(Logger.INFO, "Creating categories... SUCCESS!")
    else:
        logger.log(Logger.INFO, "Sending request for categories... FAILED!")

    return True

def import_venues(poi_file):
    venue_count = DB.query("SELECT COUNT(*) FROM " + DBSPEC.TB_VENUE + ";")[0][0]

    if venue_count > 0:
        logger.log(Logger.INFO, "Venue table already populated! " + str(venue_count) + " venues were found.")
        return

    count = 0

    with open(poi_file, 'r') as pois:
        reader = csv.reader(pois, delimiter='\t')

        for id, lat, lon, name, country in reader:
            insert_query = "INSERT INTO " + DBSPEC.TB_VENUE + """ (foursquare_id, name, geom)
            VALUES (:foursquare_id, :name, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326));"""
            insert_query = insert_query.replace(":foursquare_id", "'" + id + "'")
            insert_query = insert_query.replace(":name", "'" + name.replace("'", "''") + "'")
            insert_query = insert_query.replace(":lat", lat)
            insert_query = insert_query.replace(":lon", lon)
            DB.execute(insert_query)
            count += 1
            logger.log_dyn(Logger.INFO, "Venue '" + id + "' inserted!")

    DB.commit()
    logger.log(Logger.INFO, str(count) + " venues imported!")

def get_aware_date_time(date_str, offset):
    hours = abs(offset) // 60
    minutes = abs(offset) % 60
    str_offset = '+' if offset > 0 else '-'
    str_offset += "0" + str(hours) if hours < 10 else str(hours)
    str_offset += "0" + str(minutes) if minutes < 10 else str(minutes)
    str_date = date_str[:-10] + str_offset + " " + date_str[-4:]
    
    return datetime.strptime(str_date, '%a %b %d %H:%M:%S %z %Y')

def import_checkins(checkin_file):
    checkin_count = DB.query("SELECT COUNT(*) FROM " + DBSPEC.TB_CHECKIN + ";")[0][0]

    if checkin_count > 0:
        logger.log(Logger.INFO, "Check-in table already populated! " + str(checkin_count) + " check-ins were found.")
        return

    count = 0
    user_count = 0

    with open(checkin_file, 'r') as checkins:
        reader = csv.reader(checkins, delimiter='\t')

        for user, venue, date_time, offset in reader:
            # Gets corresponding venue ID
            venue_id = DB.query("SELECT id FROM " + DBSPEC.TB_VENUE + " WHERE foursquare_id = '" + venue + "';")[0][0]

            # Inserts the user if doesn't exist
            user_in_db = DB.query("SELECT COUNT(*) FROM " + DBSPEC.TB_ANONYMIZED_USER + " WHERE id = " + str(user) + ";")[0][0]

            if user_in_db == 0:
                DB.execute("INSERT INTO " + DBSPEC.TB_ANONYMIZED_USER + " (id, checkin_count) VALUES (" + str(user) + ", 0);")
                user_count += 1

            # Inserts the check-in
            insert_query = "INSERT INTO " + DBSPEC.TB_CHECKIN + """ (anonymized_user_id, date_time, venue_id)
            VALUES (:anonymized_user_id, :date_time, :venue_id);"""

            try:
                full_date_time = get_aware_date_time(date_time, int(offset))

                insert_query = insert_query.replace(":anonymized_user_id", str(user))
                insert_query = insert_query.replace(":date_time", "'" + str(full_date_time) + "'")
                insert_query = insert_query.replace(":venue_id", str(venue_id))
                DB.execute(insert_query)

                count += 1
                logger.log_dyn(Logger.INFO, str(count) + " check-ins imported! Current: venue " + str(venue_id) + " from user " + str(user) + ".")
            except Exception as e:
                logger.log(Logger.ERROR, str(e))
                logger.log(Logger.ERROR, "Entry (" + str(user) + ", " + str(venue) + ", " + str(date_time) + ", " + str(offset) + ") could not be processed!")

    DB.commit()
    logger.log(Logger.INFO, str(user_count) + " users imported!")
    logger.log(Logger.INFO, str(count) + " check-ins imported!")

    return True

def update_checkins_count():
    logger.log(Logger.INFO, "Updating users check-ins count... ")
    users = DB.query("""SELECT anonymized_user_id, COUNT(*) FROM """ + DBSPEC.TB_CHECKIN + """
        GROUP BY anonymized_user_id
        ORDER BY anonymized_user_id ASC""")

    for row in users:
        update_query = "UPDATE " + DBSPEC.TB_ANONYMIZED_USER + """ SET checkin_count = :count WHERE id = :id"""
        update_query = update_query.replace(":id", str(row[0]))
        update_query = update_query.replace(":count", str(row[1]))
        DB.execute(update_query)
        logger.log_dyn(Logger.INFO, "User " + str(row[0]) + " updated!")

    DB.commit()
    logger.log(Logger.INFO, "Updating users check-ins count... SUCCESS!")

def import_data(db, config, params):
    global FQ_V, FQ_PREMIUM_CALLS, FQ_REGULAR_CALLS, \
        FQ_VENUE_ENDPOINT, FQ_CATEGORY_ENDPOINT, DB

    DB = db
    FQ_V              = config['FOURSQUARE_API']['V']
    FQ_PREMIUM_CALLS  = config['FOURSQUARE_API']['PREMIUM_CALLS']
    FQ_REGULAR_CALLS  = config['FOURSQUARE_API']['REGULAR_CALLS']
    FQ_VENUE_ENDPOINT = config['FOURSQUARE_API']['VENUE_ENDPOINT']
    FQ_CATEGORY_ENDPOINT = config['FOURSQUARE_API']['CATEGORY_ENDPOINT']

    requests.config(config['FOURSQUARE_API']['CLIENT_ID'],
                    config['FOURSQUARE_API']['CLIENT_SECRET'])

    create_categories()
    import_venues(params[0])
    import_checkins(params[1])
    update_checkins_count()
