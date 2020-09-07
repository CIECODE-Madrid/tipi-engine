import re
import sys
from pathlib import Path

p = Path(__file__).parents[3]
sys.path.insert(0,str(p))

import redis

from extractors.config import REDIS_DB_DENYLIST, REDIS_HOST, REDIS_PORT


# Singleton
class RedisDenylistManager:
    __instance = None
    _conn = None

    def __init__(self):
        self._conn = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB_DENYLIST)

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.name = "Reading..."
        return cls.__instance

    def getElement(self, key):
        return self._conn.get(key)

    def addElement(self, key):
        return self._conn.set(key, key)


class Denylist:

    @staticmethod
    def getElement(key):
        return RedisDenylistManager().getElement(key)

    @staticmethod
    def addElement(key):
        return RedisDenylistManager().addElement(key)

    @staticmethod
    def isFinalState(line):
        FINAL_STATES_REGEX = [
                "caducad(a|o)",
                "rechazad(a|o)",
                "aprobad(a|o)",
                "subsumid(o|a)",
                "inadmitid(o|a)",
                "concluid(o|a)",
                "retirad(o|a)"
                ]
        control = False
        for regex in FINAL_STATES_REGEX:
            if re.search(regex, line, re.IGNORECASE):
                control = True
                break
        return control
