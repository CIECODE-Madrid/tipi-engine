import datetime
from unqlite import UnQLite
import pdb

import sys,os
from scrap.congreso.conn import MongoDBconn


class mongoItems(object):
    _conn = None
    _cursor = None
    def __init__(self):
        self._conn = MongoDBconn()
        self._cursor = self._getCollection()

    def _getCollection(self,collection="iniciativas"):
        return self._conn.getDB()[collection]

    def checkItems(self):
        allurls = UrlsScraped()
        for url in allurls.getFile():
            pdb.set_trace()


    def searchAll(self,collection="iniciativas"):
        return self._getCollection(collection).find(
            {"$and": [{"tipotexto":{"$not":re.compile('Enmienda')}}, {"tipotexto":{"$not":re.compile('Respuesta')}},{"tipotexto":{"$not":re.compile('Texto definitivo')}}]}


        )

    def countAll(self,collection="iniciativas"):
        return self._getCollection(collection).count()

import re


class UrlsScraped(object):
    __instance = None
    _file= []
    _name = "urls"
    _db= None
    _collection = None

    def __init__(self):
        self._readFile()


    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = object.__new__(cls)
            cls.__instance.name = "Reading..."
        return cls.__instance

    def _readFile(self):
        db = UnQLite('allUrls.db')
        self._db = db
        urls = db.collection('urls')
        if not urls.exists():
            urls.create()
        self._collection = urls
        self._file = urls.all()


    def getFile(self):
        #para obtener la db
        return self._db.collection('urls').all()


    def addUrl(self,url):
        self._collection.store(url)
        self._db.commit()

    def deleteAll(self):
        os.remove("allUrls.db")
        self._file = []

class CheckItems():

    @staticmethod
    def getarrayFile():
        ob = UrlsScraped()
        return ob.getFile()

    @staticmethod
    def addUrl(url):
        ob = UrlsScraped()
        ob.addUrl(url)

    @staticmethod
    def checkUrls():
        print ("Checking Items ......")
        import time


        time.sleep(5)
        ob = UrlsScraped()
        should = ob.getFile()
        con = mongoItems()
        itemsscraps = con.searchAll()
        control = False
        res = []
        toolbar_width = con.countAll()
        sys.stdout.write("[%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1))

        for item in itemsscraps:
            for url in should:
                if url == item['url']:
                    control =  True
                    break
                else:
                    control= False
            if not control:
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





