import pdb

import io
from unqlite import UnQLite




#singleton implemented
import re


class ManageFile(object):
    __instance = None
    _file= []
    _name = "blacklist"
    _db= None
    _collection = None
    _news = []

    def __init__(self):
        self._readFile()

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = object.__new__(cls)
            cls.__instance.name = "Reading..."
        return cls.__instance

    def _readFile(self):
        db = UnQLite('blacklist.db')
        self._db = db
        urls = db.collection('urls')
        if not urls.exists():
            urls.create()
        self._collection = urls
        self._file = urls.all()


    def getFile(self):
        return self._file

    def getNewsurls(self):

        return self._news




    def addUrl(self,url):
        self._news.append(url)

    def writeinDB(self):
        self._collection.store(self._news)
        self._db.commit()

    def deleteAll(self):
        self._db.flush()
        pdb.set_trace()
        self._db.commit()







class Blacklist():


    @staticmethod
    def getarrayFile():
        file = ManageFile()

        return file.getFile()

    @staticmethod
    def getNewsurls():
        file = ManageFile()

        return file.getNewsurls()




    @staticmethod
    def writeFile():
        file = ManageFile()
        file.writeinDB()
        del file

    @staticmethod
    def addUrl(url):
        file = ManageFile()
        file.addUrl(url)

    @staticmethod
    def isAddedtolist(line):
        rexps= ["caducad(a|o)","rechazad(a|o)","aprobad(a|o)","subsumid(o|a)"
                ,"inadmitid(o|a)","concluid(o|a)","retirad(o|a)"]

        control = False
        for rege in rexps:
            if rege is "tramitad(o|a)":
                pass
            if re.search(rege,line,re.IGNORECASE):
                control= True
                break
        return control








