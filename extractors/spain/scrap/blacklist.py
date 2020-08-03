import re
from importlib import import_module as im

import redis

from extractors.config import REDIS_DB_BLACKLIST, REDIS_HOST, REDIS_PORT


# Singleton
class RedisBlacklistManager:
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


class Blacklist:

    @staticmethod
    def getElement(key):
        return RedisBlacklistManager().getElement(key)

    @staticmethod
    def addElement(key):
        return RedisBlacklistManager().addElement(key)

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
