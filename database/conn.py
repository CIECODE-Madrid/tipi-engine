# -*- coding: utf-8 -*-
import pymongo

from settings import MongoConfig
import pdb



class MongoDBconn(object):
    __instance = None
    _client = None
    _currentDB = None

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = object.__new__(cls)
            cls.__instance.name = "Reading..."
        return cls.__instance

    def __init__(self):
        self._connDB()

    def _connDB(self):
        configuration = MongoConfig()
        mongo_client = pymongo.MongoClient(host=configuration.host, port=configuration.port)
        self._client = mongo_client
        try:
            db = mongo_client[configuration.db_name]
            if configuration.username is not None:
                db.authenticate(configuration.username, password=configuration.password)
            self._currentDB = db
        except:
            pass

    def getConn(self):
        return self._client

    def getDB(self):
        return self._currentDB

    def closeDB(self):
        self._client.close()
        self.__instance = None




