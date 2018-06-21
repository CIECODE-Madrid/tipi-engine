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
        for status in STATUS_MAP.keys():
            status_keys = STATUS_MAP[status].keys()
            status_search = dict()
            for status_key in status_keys:
                aux_status_key = status_key
                if aux_status_key is 'processing':
                    aux_status_key = '$or'
                status_search[aux_status_key] = self._process_status_key(status, status_key)
            dbmanager.updateInitiativesStatus(status_search, status)

    def _process_status_key(self, status, status_key):
        if status_key is 'processing':
            processing_array = []
            for processing in STATUS_MAP[status][status_key]:
                processing_array.append(
                        {'processing': {'$regex': processing, '$options': 'gi'}}
                    )
            return processing_array
        return {'$in': STATUS_MAP[status][status_key]}
