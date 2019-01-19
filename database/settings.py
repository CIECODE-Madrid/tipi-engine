import pymongo
from .variables import config


class Config(object):
    def __init__(self):
        self._config = config

    def get_property(self, property_name):
        if property_name not in self._config.keys():
            return None
        return self._config[property_name]


class MongoConfig(Config):
    @property
    def host(self):
        return self.get_property('MONGO_HOST')

    @property
    def port(self):
        return self.get_property('MONGO_PORT')

    @property
    def username(self):
        return self.get_property('MONGO_USERNAME')

    @property
    def db_name(self):
        return self.get_property('MONGO_DB_NAME')

    @property
    def password(self):
        return self.get_property('MONGO_PASSWORD')

