import logging
import time
from datetime import datetime

import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed

from tipi_data.models.initiative import Initiative

from .api import ENDPOINT
from .legislative_period import LegislativePeriod


log = logging.getLogger(__name__)


def initiative_parse_date(str_date):
    split_date = str_date.split('/')
    if len(split_date) is not 3:
        return None
    return datetime(int(split_date[2]),int(split_date[1]),int(split_date[0]))


class InitiativesExtractor:
    def __init__(self):
        self.__legislative_period = LegislativePeriod().get()

    def __create_or_update(self, remote_initiative):
        initiative = Initiative(
                id=str(remote_initiative['idProyecto']),
                reference=str(remote_initiative['idProyecto']),
                title=remote_initiative['acapite'],
                initiative_type=remote_initiative['tipoProyecto'],
                author_deputies=self.__get_authors(remote_initiative['idProyecto']),
                processing="{} ({})".format(remote_initiative['descripcionEtapa'], remote_initiative['descripcionSubEtapa']),
                status=remote_initiative['estadoProyecto'],
                created=initiative_parse_date(remote_initiative['fechaIngresoExpediente']),
                updated=initiative_parse_date(remote_initiative['fechaIngresoExpediente'])
                )
        initiative.save()
        log.info("Iniciativa {} procesada".format(str(remote_initiative['idProyecto'])))


    def __get_authors(self, expedient_id):
        response = requests.get(ENDPOINT.format(method='proyecto/{}/autores'.format(expedient_id)))
        if 'listaAutores' not in response.json().keys():
            return []
        return [str(author['idParlamentario']) for author in response.json()['listaAutores']]


    def __get_total(self):
        response = requests.get(ENDPOINT.format(method='proyecto/total'))
        if not response.ok:
            return 0
        return int(response.content)

    def extract(self):
        per_page = 20
        urls = [
                ENDPOINT.format(method="proyecto?offset={}&limit={}".format(offset, per_page))
                for offset in range(1, (int(self.__get_total()/per_page)+1)+1)
                ]

        start_time = time.time()
        with FuturesSession() as session:
            futures = [session.get(url) for url in urls]
            for future in as_completed(futures):
                response = future.result()
                for initiative in response.json():
                    # extra.origen = expedient['origenProyecto']
                    # extra.observaciones = expedient['iniciativa']
                    self.__create_or_update(initiative)
        print("--- %s seconds ---" % (time.time() - start_time))
