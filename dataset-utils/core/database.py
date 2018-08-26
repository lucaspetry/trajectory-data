import psycopg2
from core.logger import Logger


class Database(object):

    _dbname = ""
    _dbhost = ""
    _dbuser = ""
    _dbpass = ""
    _conn = None
    _logger = Logger()
    _status = "None"

    def status(self):
        return self._status

    def config(self, name, host, user, passwd):
        self._dbname = name
        self._dbhost = host
        self._dbuser = user
        self._dbpass = passwd

    def connect(self):
        try:
            self._conn = psycopg2.connect("dbname='" + self._dbname +
                                          "' user='" + self._dbuser +
                                          "' host='" + self._dbhost +
                                          "' password='" + self._dbpass + "'")
            self._status = "Connected"
            return True
        except Exception as e:
            self._status = str(e)
            return False

    def close(self):
        self._conn.close()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def query(self, query):
        cur = self._conn.cursor()
        try:
            cur.execute(query)
            return cur.fetchall()
        except Exception as e:
            self._logger.log(Logger.ERROR, "Query execution failed for query '" + query[0:50] + "...'")
            self._logger.log(Logger.ERROR, str(e))
            raise

    def execute(self, query):
        cur = self._conn.cursor()
        try:
            cur.execute(query)
        except Exception as e:
            self._logger.log(Logger.ERROR, "Query execution failed for query '" + query[0:50] + "...'")
            self._logger.log(Logger.ERROR, str(e))
            raise
