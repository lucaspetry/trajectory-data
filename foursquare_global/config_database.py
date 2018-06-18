import sys
import configparser
from core.database import Database
from core.logger import Logger
from init_database import import_data
from update_database import update_venues

logger = Logger()


########################## MISC ##########################
def print_valid_ops():
    logger.log(Logger.INFO, """Valid operations:
    		create  -  creates the database schema and populates basic info (no params)
    		drop    -  drops the database schema (no params)
    		init    -  imports data from file to database (params = poi_file checkin_file)
    		update  -  update venue information from Foursquare API (params = reset/resume)""")
##########################################################


####################### ARGS CHECK #######################
if(len(sys.argv) < 3):
    logger.log(Logger.ERROR, "Please inform the configuration file and the desired operation!")
    logger.log(Logger.ERROR, "Example: python3 config_database.py config.ini op params")
    print_valid_ops()
    exit()
##########################################################


######################### PARAMS #########################
VALID_OPS = ['create', 'drop', 'init', 'update']
OPS_PARAMS = [0, 0, 2, 1]
CREATE_SCHEMA_FILE = 'sql/create_schema.sql'
DROP_SCHEMA_FILE = 'sql/drop_schema.sql'

CONFIG_FILE = sys.argv[1]
OPERATION = sys.argv[2]
PARAMS = [sys.argv[i] for i in range(3, len(sys.argv))]

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

db = Database()
db.config(config['DATABASE']['NAME'],
          config['DATABASE']['HOST'],
          config['DATABASE']['USER'],
          config['DATABASE']['PASS'])
##########################################################


######################## OP CHECK ########################
if OPERATION not in VALID_OPS:
	logger.log(Logger.ERROR, "Invalid operation!")
	print_valid_ops()
	exit()

if OPS_PARAMS[VALID_OPS.index(OPERATION)] != len(PARAMS):
	logger.log(Logger.ERROR, "Invalid number of parameters!")
	print_valid_ops()
	exit()
##########################################################


####################### OP HANDLE ########################
if(db.connect()):
    logger.log(Logger.INFO, "Succesfully connected to database \'" + str(config['DATABASE']['NAME']) + "\'!")
else:
    logger.log(Logger.INFO, "Failed connecting to database \'" + str(config['DATABASE']['NAME']) + "\'!")


if OPERATION == 'create':
	logger.log_dyn(Logger.INFO, "Creating schema for database '" + str(config['DATABASE']['NAME']) + "'... ")
	db.execute(open(CREATE_SCHEMA_FILE, "r").read())
	db.commit()
	logger.log(Logger.INFO, "Creating schema for database '" + str(config['DATABASE']['NAME']) + "'... SUCCESS!")

	db.close()
	exit()
elif OPERATION == 'drop':
	option = logger.get_answer("The drop option will clear the database and drop all" + \
			" existing tables. Do you want to continue? (y/N) ").lower()

	if option != 'y':
		exit()

	logger.log_dyn(Logger.INFO, "Dropping schema for database '" + str(config['DATABASE']['NAME']) + "'... ")
	db.execute(open(DROP_SCHEMA_FILE, "r").read())
	db.commit()
	logger.log(Logger.INFO, "Dropping schema for database '" + str(config['DATABASE']['NAME']) + "'... SUCCESS!")
	db.close()
	exit()
elif OPERATION == 'init':
	logger.log(Logger.INFO, "Initializing database '" + str(config['DATABASE']['NAME']) + "'... ")
	import_data(db, config, PARAMS)
	logger.log(Logger.INFO, "Initializing database '" + str(config['DATABASE']['NAME']) + "'... SUCCESS!")
	exit()
elif OPERATION == 'update':
	if PARAMS[0] == 'reset':
		option = logger.get_answer("The reset option will clear all venues" + \
			" updated dates and will update them. Do you want to continue? (y/N) ").lower()

		if option != 'y':
			exit()

	update_venues(PARAMS)
##########################################################
