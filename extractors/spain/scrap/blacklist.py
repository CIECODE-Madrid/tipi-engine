#singleton implemented
import re
import sys
from pathlib import Path
p = Path(__file__).parents[3]
sys.path.insert(0,str(p))

import redis

from extractors.config import REDIS_DB_BLACKLIST, REDIS_HOST, REDIS_PORT


class ManageRedisBlackList(object):
    __instance = None
    _conn = None

    def __init__(self):
        self._conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB_BLACKLIST)

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = object.__new__(cls)
            cls.__instance.name = "Reading..."
        return cls.__instance


    def getElement(self,key):
        return self._conn.get(key)

    def addElement(self,key):
        return self._conn.set(key,key)


class Blacklist():

    @staticmethod
    def getElement(key):
        file = ManageRedisBlackList()

        return file.getElement(key)

    @staticmethod
    def addElement(key):
        file = ManageRedisBlackList()

        return file.addElement(key)


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
