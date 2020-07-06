# singleton implemented
import re
import sys
from pathlib import Path

import redis

from extractors.config import REDIS_DB_BLACKLIST, REDIS_HOST, REDIS_PORT


p = Path(__file__).parents[3]
sys.path.insert(0, str(p))


class ManageRedisBlackList(object):
    __instance = None
    _conn = None

    def __init__(self):
        self._conn = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB_BLACKLIST)

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.name = "Reading..."
        return cls.__instance

    def getElement(self, key):
        return self._conn.get(key)

    def addElement(self, key):
        return self._conn.set(key, key)


class Blacklist():

    @staticmethod
    def getElement(key):
        return ManageRedisBlackList().getElement(key)

    @staticmethod
    def addElement(key):
        return ManageRedisBlackList().addElement(key)

    @staticmethod
    def isFinalState(line):
        regex_list = ["caducad(a|o)", "rechazad(a|o)", "aprobad(a|o)",
                "subsumid(o|a)", "inadmitid(o|a)", "concluid(o|a)",
                "retirad(o|a)"]

        control = False
        for regex in regex_list:
            if re.search(regex, line, re.IGNORECASE):
                control = True
                break
        return control
