import datetime
import sys
import re
import redis
from pathlib import Path

from database.conn import MongoDBconn
from extractors.config import REDIS_DB_CHECK, REDIS_HOST, REDIS_PORT


p = Path(__file__).parents[3]
sys.path.insert(0, str(p))


class mongoItems(object):

    _conn = None
    _cursor = None

    def __init__(self):
        self._conn = MongoDBconn()
        self._cursor = self._getCollection()

    def _getCollection(self, collection="iniciativas"):
        return self._conn.getDB()[collection]

    def searchbyUrl(self, url):

        return self._getCollection("initiatives").find(
                {"$and": [
                    {'url': url},
                    {"initiative_type_alt": {"$not": re.compile('Enmienda')}},
                    {"initiative_type_alt": {"$not": re.compile('Respuesta')}},
                    {"initiative_type_alt": {"$not": re.compile('Texto definitivo')}}
                    ]}
                ).count()


class UrlsScraped(object):

    __instance = None
    _conn = None

    def __init__(self):
        self._conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB_CHECK)

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.name = "Reading..."
        return cls.__instance

    def getElement(self, key):
        return self._conn.get(key)

    def getScan(self):
        return self._conn.scan_iter()

    def addElement(self, key):
        return self._conn.set(key, key)

    def deletedb(self):
        return self._conn.flushdb()


class CheckItems():

    @staticmethod
    def getElement(key):
        return UrlsScraped().getElement(key)

    @staticmethod
    def addElement(key):
        return UrlsScraped().addElement(key)

    @staticmethod
    def deleteDb():
        return UrlsScraped().deletedb()

    @staticmethod
    def checkUrls():
        print("Checking Items ......")
        import time
        time.sleep(5)
        con = mongoItems()
        iterredis = UrlsScraped().getScan()
        res = []
        for url in iterredis:
            if con.searchbyUrl(url) == 0:
                res.append(url)
        print("Reporting Error ......")
        # Writing file
        CheckItems.writelogfailed(res)
        return res

    @staticmethod
    def writelogfailed(array):
        import logging
        LOG_FILENAME = 'failed.log'
        logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
        logging.FileHandler(LOG_FILENAME)
        f = open(LOG_FILENAME, 'w')
        f.write(" {} ".format(datetime.datetime.now()))
        for url in array:
            logging.error(url)
            f.write(str(url))


class CheckSystem(object):

    @staticmethod
    def systemlog(msg):
        import logging
        LOG_FILENAME = 'system.log'
        logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
        logging.FileHandler(LOG_FILENAME)
        f = open(LOG_FILENAME, 'a')
        f.write(" {} ".format(datetime.datetime.now()))
        logging.error(msg)
        f.write(msg)
