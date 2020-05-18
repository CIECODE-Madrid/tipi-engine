import logging

import requests
from tipi_data.models.deputy import Deputy

from .api import ENDPOINT
from .legislative_period import LegislativePeriod


log = logging.getLogger(__name__)


class MembersExtractor:
    def __init__(self):
        self.__legislative_period = LegislativePeriod().get()

    def __create_or_update(self, remote_member):
        member = Deputy(
                id=str(remote_member['idParlamentario']),
                name="{} {}".format(remote_member['nombres'].title(), remote_member['apellidos'].title()),
                parliamentarygroup=remote_member['partidoPolitico'],
                image=remote_member['fotoURL'],
                email=remote_member['emailParlamentario'],
                web=None,
                twitter=None,
                start_date=None,
                end_date=None,
                url=remote_member['appURL'],
                active=False
                )
        member.save()
        log.info("Parlamentario {} procesado".format(str(remote_member['idParlamentario'])))


    def __refresh_all_members(self):
        response = requests.get(ENDPOINT.format(method='parlamentario'))
        for member in response.json():
            self.__create_or_update(member)


    def __update_active_members(self, chamber='S'):
        response = requests.get(ENDPOINT.format(method='parlamentario/camara/{}'.format(chamber)))
        for mp in response.json():
            try:
                member = Deputy.objects.get(id=str(mp['idParlamentario']))
                member.active = True
                member.save()
            except Deputy.DoesNotExist:
                log.warning("Extracting members: Deputy does not exists with id {}".format(id))
            except Deputy.MultipleObjectsReturned:
                log.warning("Extracting members: Multiple objects returned for id {}".format(id))


    def extract(self):
        self.__refresh_all_members()
        for chamber in ['S', 'D']:
            self.__update_active_members(chamber)
