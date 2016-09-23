import datetime
import sys,os
import redis
import pdb
from pathlib import Path

p = Path(__file__).parents[4]
sys.path.insert(0,str(p))
from database.conn import MongoDBconn

class mongoItems(object):
    _conn = None
    _cursor = None
    def __init__(self):
        self._conn = MongoDBconn()
        self._cursor = self._getCollection()

    def _getCollection(self,collection="iniciativas"):
        return self._conn.getDB()[collection]


    def searchAll(self,collection="iniciativas"):
        return self._getCollection(collection).find(
            {"$and": [{"tipotexto":{"$not":re.compile('Enmienda')}}, {"tipotexto":{"$not":re.compile('Respuesta')}},{"tipotexto":{"$not":re.compile('Texto definitivo')}}]}


        )

    def countAll(self,collection="iniciativas"):
        return self._getCollection(collection).count()

import re


class UrlsScraped(object):
    __instance = None
    _conn=None

    def __init__(self):
        self._conn = redis.Redis(
                        host='localhost',
                        port=6379,
                        db=1)

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = object.__new__(cls)
            cls.__instance.name = "Reading..."
        return cls.__instance

    def getElement(self,key):
        return self._conn.get(key)

    def addElement(self,key):
        return self._conn.set(key,key)

    def deleteAll(self):
        return self._conn.flushdb()




class CheckItems():
    @staticmethod
    def getElement(key):
        file = UrlsScraped()

        return file.getElement(key)

    @staticmethod
    def addElement(key):
        file = UrlsScraped()

        return file.addElement(key)

    @staticmethod
    def checkUrls():
        print ("Checking Items ......")
        import time


        time.sleep(5)
        ob = UrlsScraped()

        con = mongoItems()
        itemsscraps = con.searchAll()
        control = False
        res = []
        toolbar_width = con.countAll()
        sys.stdout.write("[%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1))

        for item in itemsscraps:

            if ob.getElement(item['url']):
                break
            else:
                res.append(item['url'])
            sys.stdout.write("-")
            sys.stdout.flush()

        sys.stdout.write("\n")
        ob.deleteAll()
        del ob
        print ("Reporting Error ......")
        #escribe fichero
        CheckItems.writelogfailed(res)


        return res

    @staticmethod
    def writelogfailed(array):
        import logging
        LOG_FILENAME = 'failed.log'
        logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
        logging.FileHandler(LOG_FILENAME)
        f = open(LOG_FILENAME, 'w')
        f.write((" %s " % datetime.datetime.now())+"\n")
        for url in array:
            logging.error(url)
            f.write(url+"\n")



class CheckSystem(object):
    @staticmethod
    def systemlog(msg):
        import logging
        LOG_FILENAME = 'system.log'
        logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
        logging.FileHandler(LOG_FILENAME)
        f = open(LOG_FILENAME, 'a')
        f.write((" %s " % datetime.datetime.now())+"\n")
        logging.error(msg)
        f.write(msg+"\n")





