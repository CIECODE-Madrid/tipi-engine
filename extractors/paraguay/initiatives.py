import logging
import re
import time
from datetime import datetime
from os.path import splitext
import tempfile

import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
from textract import process

from tipi_data.models.initiative import Initiative

from .api import ENDPOINT
from .legislative_period import LegislativePeriod
from .initiatives_attachments import MIMETYPE_FILE_EXTENSIONS


log = logging.getLogger(__name__)


class InitiativesExtractor:
    def __init__(self):
        self.__legislative_period = LegislativePeriod().get()

    def __get_total(self):
        response = requests.get(ENDPOINT.format(method='proyecto/total'))
        if not response.ok:
            return 0
        return int(response.content)

    def extract(self):
        per_page = 20
        ROUNDING_UP = BOUNDARY = 1
        urls = [
                ENDPOINT.format(method="proyecto?offset={}&limit={}".format(offset, per_page))
                for offset in range(1, (int(self.__get_total()/per_page))+ROUNDING_UP+BOUNDARY)
                ]
        with FuturesSession() as session:
            futures = [session.get(url) for url in urls]
            for future in as_completed(futures):
                response = future.result()
                for initiative in response.json():
                    self.__create_or_update(initiative)

    def __create_or_update(self, remote_initiative):
        initiative = Initiative(
                id=str(remote_initiative['idProyecto']),
                reference=str(remote_initiative['expedienteCamara']),
                title=remote_initiative['acapite'],
                initiative_type=remote_initiative['tipoProyecto'],
                processing="{} ({})".format(
                    remote_initiative['descripcionEtapa'],
                    remote_initiative['descripcionSubEtapa']
                    ),
                status=remote_initiative['estadoProyecto'],
                topics=[],
                tags=[],
                tagged=False,
                url=remote_initiative['appURL'],
                created=self.__parse_date(remote_initiative['fechaIngresoExpediente']),
                updated=self.__parse_date(remote_initiative['fechaIngresoExpediente'])
                )
        initiative['extra'] = dict()
        initiative['extra']['origen'] = remote_initiative['origenProyecto']
        initiative['extra']['observaciones'] = remote_initiative['iniciativa']
                    # extra.observaciones = expedient['iniciativa']
        self.__load_more_data(initiative)
        initiative.save()
        log.info("Iniciativa {} procesada".format(str(remote_initiative['idProyecto'])))

    def __load_more_data(self, initiative):
        response = requests.get(ENDPOINT.format(method='proyecto/{}/detalle'.format(initiative['id'])))
        self.__load_authors_from_response(initiative, response)
        # self.__load_content_from_response(initiative, response)
        initiative['content'] = []

    def __load_authors_from_response(self, initiative, response):
        author_deputies = []
        if 'listaAutores' in response.json().keys():
            author_deputies = [
                    "{} {} [{}]".format(
                        author['nombres'].strip().title(),
                        author['apellidos'].strip().title(),
                        author['idParlamentario'])
                    for author in response.json()['listaAutores']
                    ]
            initiative['author_deputies'] = author_deputies
        if 'ministerios' in response.json().keys():
            initiative['author_others'] = response.json()['ministerios']

    def __load_content_from_response(self, initiative, response):
        if 'archivosAdjuntos' in response.json().keys():
            attachments = response.json()['archivosAdjuntos']
            for attachment in attachments:
                response = requests.get(attachment['appURL'])
                if response.ok:
                    try:
                        with tempfile.NamedTemporaryFile(suffix=MIMETYPE_FILE_EXTENSIONS[attachment['tipoArchivo']]) as f:
                            f.write(bytes(response.content))
                            try:
                                content = process(f.name).decode('utf-8').strip()
                                content = content.replace('\n', ' ').replace('\f', ' ').replace('\t', '')
                                content = [x for x in re.split(r'\.(?!\d)', content) if x != '']
                            except Exception:
                                content = []
                            else:
                            f.close()
                        initiative['content'] = content
                        initiative['extra']['content_reference'] = "{} - {}".format(
                                attachment['infoAdjunto'],
                                attachment['tipoAdjunto'])
                        break
                    except KeyError:
                        # Mimetype not found in our list
                        pass

    def __parse_date(self, str_date):
        split_date = str_date.split('/')
        if len(split_date) != 3:
            return None
        return datetime(int(split_date[2]), int(split_date[1]), int(split_date[0]))
