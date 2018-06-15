from core.database import Database
from core.logger import Logger

logger = Logger()
DB = None
FQ_V = None
FQ_PREMIUM_CALLS = None
FQ_REGULAR_CALLS = None
FQ_VENUE_ENDPOINT = None
FQ_CATEGORY_ENDPOINT = None


def update_venues(params):
    global FQ_V, FQ_PREMIUM_CALLS, FQ_REGULAR_CALLS, \
        FQ_VENUE_ENDPOINT, FQ_CATEGORY_ENDPOINT, DB

    DB = db
    FQ_V              = config['FOURSQUARE_API']['V']
    FQ_PREMIUM_CALLS  = config['FOURSQUARE_API']['PREMIUM_CALLS']
    FQ_REGULAR_CALLS  = config['FOURSQUARE_API']['REGULAR_CALLS']
    FQ_VENUE_ENDPOINT = config['FOURSQUARE_API']['VENUE_ENDPOINT']
    FQ_CATEGORY_ENDPOINT = config['FOURSQUARE_API']['CATEGORY_ENDPOINT']

	logger.log(Logger.INFO, "TO-DO")