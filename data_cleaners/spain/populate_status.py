from time import time
import itertools
import pymongo

from tipi_data.models.initiative import Initiative

from .status_map import STATUS_MAP


class PopulateStatus:

    def populate(self):
        for status_element in STATUS_MAP:
            Initiative.all(
                    __raw__=status_element['search']).update(
                            status=status_element['status'])
