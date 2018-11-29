# Ths Python file uses the following encoding: utf-8
import sys
from time import time
import itertools
import pymongo 

from .status_map import STATUS_MAP
from database.congreso import Congress

reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')


class PopulateStatus:

    def populate(self):
        dbmanager = Congress()
        for status_element in STATUS_MAP:
            dbmanager.updateInitiativesStatus(status_element['search'], status_element['status'])
