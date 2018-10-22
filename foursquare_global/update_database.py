from core.logger import Logger
from db_spec import DBSPEC
from datetime import datetime
from pytz import reference
import time
import json
import os

logger = Logger()
country_dict = {}


def update_venue_from_dict(db, foursquare_id, data, get_date_time):
    query = "UPDATE " + DBSPEC.TB_VENUE + " SET date_time_updated = ':updated'"

    for col in data.keys():
        query += ', ' + col + ' = ' + str(data[col])

    query += " WHERE foursquare_id = ':foursquare_id'"
    query = query.replace(":updated", str(get_date_time))
    query = query.replace(":foursquare_id", foursquare_id)
    db.execute(query)


def insert_venue_from_dict(db, data, get_date_time):
    query = "INSERT INTO " + DBSPEC.TB_VENUE + " (:keys) VALUES(:values)"
    keys = "date_time_updated"
    values = "'" + str(get_date_time) + "'"

    for col in data.keys():
        keys += ', ' + col
        values += ', ' + str(data[col])

    query = query.replace(":keys", keys)
    query = query.replace(":values", values)
    db.execute(query)


def add_get_city(db, data):
    if 'city' not in data:
        return 'NULL'

    country_id = country_dict[data['cc']]
    city = data['city']
    state = data['state'] if 'state' in data else 'NULL'
    city_query = "SELECT id FROM geo_city WHERE name = $$:name$$ AND " + \
                 "state = $$:state$$ AND country_id = :country_id"
    city_query = city_query.replace(":name", city)
    city_query = city_query.replace(":state", state)
    city_query = city_query.replace(":country_id", str(country_id))
    res = db.query(city_query)

    if len(res) > 0:
        return res[0][0]

    insert_query = "INSERT INTO geo_city(name, state, country_id) " + \
                   "VALUES ($$:name$$, $$:state$$, :country_id)"
    insert_query = insert_query.replace(":name", city)
    insert_query = insert_query.replace(":state", state)
    insert_query = insert_query.replace(":country_id", str(country_id))
    db.execute(insert_query)

    res = db.query(city_query)
    return res[0][0]


def add_get_parent(db, data, get_date_time):
    venue_query = "SELECT id FROM fq_venue WHERE foursquare_id = " + \
                  "':foursquare_id'"
    venue_query = venue_query.replace(":foursquare_id", data['id'])
    res = db.query(venue_query)

    if len(res) > 0:
        return res[0][0]

    location = data['location']

    venue = {
        'foursquare_id': "'" + data['id'] + "'",
        'name': "$tag$" + data['name'] + "$tag$",
        'geom': 'ST_SetSRID(ST_MakePoint(' + str(location['lng']) + ', ' +
                str(location['lat']) + '), 4326)',
        'city_id': add_get_city(db, data['location']),
        'address': "$tag$" + location['address'] + "$tag$" if 'address' in location else 'NULL',
        'postal_code': "'" + location['postalCode'] + "'" if 'postalCode' in location else 'NULL',
    }
    insert_venue_from_dict(db, venue, get_date_time)
    link_categories(db, data['id'], data['categories'])
    return db.query(venue_query)[0][0]


def link_categories(db, foursquare_id, cats):
    insert_query = "INSERT INTO fq_venue_category VALUES ((SELECT id " + \
                   "FROM fq_venue WHERE foursquare_id = ':foursquare_id')," + \
                   "(SELECT id FROM fq_category WHERE foursquare_id = " + \
                   " ':cat_foursquare_id'), :is_primary)"
    insert_query = insert_query.replace(':foursquare_id', str(foursquare_id))
    done = []

    for cat in cats:
        if cat['id'] in done or cat['id'] == '52f2ab2ebcbc57f1066b8b52':
            continue

        done.append(cat['id'])
        primary = cat['primary'] if 'primary' in cat else False
        cur_query = insert_query.replace(':cat_foursquare_id', cat['id'])
        cur_query = cur_query.replace(':is_primary', str(primary))
        db.execute(cur_query)


def update_venue(db, foursquare_id, data, get_date_time):
    venue = data['response']['venue']
    contact = venue['contact']
    location = venue['location']

    dict_data = {
        'parent_id': add_get_parent(db, venue['parent'], get_date_time) if 'parent' in venue
                                                            else 'NULL',
        'geom': 'ST_SetSRID(ST_MakePoint(' + str(location['lng']) + ', ' +
                str(location['lat']) + '), 4326)',
        'city_id': add_get_city(db, location),
        'address': "$tag$" + location['address'] + "$tag$" if 'address' in location else 'NULL',
        'postal_code': "'" + location['postalCode'] + "'" if 'postalCode' in location else 'NULL',
        'time_zone': '$tag$' + venue['timeZone'] + '$tag$',
        'name': '$tag$' + venue['name'] + '$tag$',
        'phone': '$tag$' + contact['phone'] + '$tag$' if 'phone' in contact else 'NULL',
        'twitter': "'" + contact['twitter'] + "'" if 'twitter' in contact else 'NULL',
        'instagram': "'" + contact['instagram'] + "'" if 'instagram' in contact else 'NULL',
        'facebook': "'" + contact['facebook'] + "'" if 'facebook' in contact else 'NULL',
        'url': '$tag$' + venue['url'] + '$tag$' if 'url' in venue else 'NULL',
        'verified': venue['verified'],
        'created_at': "'" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(venue['createdAt'])) + "'",
        'checkins_count': venue['stats']['checkinsCount'] if 'checkinsCount' in venue['stats'] else 'NULL',
        'likes_count': venue['likes']['count'] if 'likes' in venue else 'NULL',
        'users_count': venue['stats']['usersCount'] if 'usersCount' in venue['stats'] else 'NULL',
        'tips_count': venue['tips']['count'],
        'photos_count': venue['photos']['count'],
        'listed_count': venue['listed']['count'],
        'rating': venue['rating'] if 'rating' in venue else 'NULL',
        'price_tier': venue['price']['tier'] if 'price' in venue else 'NULL',
        'hours': '$tag$' + str(venue['hours']) + '$tag$' if 'hours' in venue else 'NULL',
        'popular_hours': '$tag$' + str(venue['popular']) + '$tag$' if 'popular' in venue else 'NULL',
        'attributes': '$tag$' + str(venue['attributes']) + '$tag$'
        # 'atm': 0,
        # 'coat_check': 0,
        # 'outdoor_seating': 0,
        # 'credit_cards': 0,
        # 'smoking': 0,
        # 'restroom': 0,
        # 'music': 0,
        # 'music_live': 0,
        # 'music_jukebox': 0,
        # 'wheelchair_accessible': 0,
        # 'tvs': 0,
        # 'wifi': 0,
        # 'wifi_paid': 0,
        # 'parking': 0,
        # 'parking_type': 0,
        # 'reservations_nongroup': 0,
        # 'reservations_group': 0,
        # 'private_room': 0,
        # 'dining_delivery': 0,
        # 'dining_drive_thru': 0,
        # 'dining_bar_service': 0,
        # 'dining_table_service': 0,
        # 'dining_take_out': 0,
        # 'menu_breakfast': 0,
        # 'menu_lunch': 0,
        # 'menu_brunch': 0,
        # 'menu_dinner': 0,
        # 'menu_dessert': 0,
        # 'menu_happy_hour': 0,
        # 'menu_bar_snacks': 0,
        # 'drinks_beer': 0,
        # 'drinks_cocktails': 0,
        # 'drinks_wine': 0,
        # 'drinks_full_bar': 0
    }
    update_venue_from_dict(db, foursquare_id, dict_data, get_date_time)
    link_categories(db, foursquare_id, venue['categories'])
    db.commit()
    logger.log(Logger.INFO, "Venue '" + foursquare_id + "' updated!")


def is_up_to_date(db, foursquare_id, get_date_time):
    query = "SELECT date_time_updated FROM " + DBSPEC.TB_VENUE + " WHERE " + \
            "foursquare_id = ':foursquare_id'"
    query = query.replace(":foursquare_id", foursquare_id)
    date_time = db.query(query)[0][0]
    return date_time == get_date_time


def update_venues(db, config, folder, reset=False):
    global country_dict

    venue_files = sorted(os.listdir(folder))
    country_dict = dict(db.query("SELECT code, id FROM geo_country"))

    if reset:
        logger.log(Logger.INFO, "Reseting timestamp updates... ")
        db.execute("UPDATE " + DBSPEC.TB_VENUE +
                   " SET date_time_updated = NULL")
        logger.log(Logger.INFO, "Reseting timestamp updates... SUCCESS!")
        logger.log(Logger.INFO, "Deleting category links... ")
        db.execute("UPDATE " + DBSPEC.TB_VENUE +
                   " SET date_time_updated = NULL")
        logger.log(Logger.INFO, "Deleting category links... SUCCESS!")
        db.commit()

    for file in venue_files:
        file_path = folder + "/" + file
        foursquare_id = file.replace(".json", "")

        localtime = reference.LocalTimezone()
        modified_timestamp = datetime.fromtimestamp(
            os.path.getmtime(file_path))
        modified_timestamp = modified_timestamp.replace(tzinfo=localtime)

        data = None

        with open(file_path) as f:
            data = json.load(f)

        if is_up_to_date(db, foursquare_id, modified_timestamp):
            logger.log_dyn(Logger.WARNING, "Venue '" + foursquare_id +
                           "' is up to date. Skipping...")
            continue

        try:
            update_venue(db, foursquare_id, data, modified_timestamp)
        except Exception as e:
            db.rollback()
            logger.log(Logger.ERROR, str(e))

    logger.log(Logger.INFO, "All venues updated!")
