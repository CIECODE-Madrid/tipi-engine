import re
from datetime import datetime
import tempfile

import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
from textract import process

from tipi_data.models.initiative import Initiative

from logger import get_logger
from extractors.blacklist import Blacklist
from .api import ENDPOINT
from .legislative_period import LegislativePeriod
from .initiatives_attachments import MIMETYPE_FILE_EXTENSIONS, \
                                     ATTACHMENTS_WORKFLOW, \
                                     get_current_phase, \
                                     get_next_phase


log = get_logger(__name__)


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
                    if not Blacklist.getElement(initiative['idProyecto']):
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
                place=remote_initiative['origenProyecto'],
                topics=[],
                tags=[],
                tagged=False,
                url=remote_initiative['appURL'],
                created=self.__parse_date(remote_initiative['fechaIngresoExpediente']),
                updated=self.__parse_date(remote_initiative['fechaIngresoExpediente'])
                )
        initiative['extra'] = dict()
        initiative['extra']['proponente'] = remote_initiative['iniciativa']
        self.__load_more_data(initiative)
        initiative.save()
        try:
            if Blacklist.isFinalState(initiative['status']):
                Blacklist.addElement(initiative['id'])
        except Exception as e:
            log.warning("Error adding an expedient to Blacklist: {}".format(e))
        log.info("Iniciativa {} procesada".format(str(remote_initiative['idProyecto'])))

    def __load_more_data(self, initiative):
        response = requests.get(ENDPOINT.format(method='proyecto/{}/detalle'.format(initiative['id'])))
        self.__load_authors_from_response(initiative, response)
        self.__load_content_from_response(initiative, response)

    def __load_authors_from_response(self, initiative, response):
        if 'listaAutores' in response.json().keys():
            initiative['author_deputies'] = [
                    "{} {} [{}]".format(
                        author['nombres'].strip().title(),
                        author['apellidos'].strip().title(),
                        author['idParlamentario'])
                    for author in response.json()['listaAutores']
                    ]
            initiative['author_parliamentarygroups'] = list({
                    author['partidoPolitico']
                    for author in response.json()['listaAutores']
                    })
        if 'ministerios' in response.json().keys():
            initiative['author_others'] = response.json()['ministerios']

    def __load_content_from_response(self, initiative, response):
        response = response.json()
        if 'archivosAdjuntos' in response.keys():
            current_phase, current_phase_counter = get_current_phase(str(response['idProyecto']))
            next_phase_index, next_phase = get_next_phase(current_phase)
            if next_phase_index != -1:
                attachments = response['archivosAdjuntos']
                if current_phase_counter < len([a for a in attachments if a['infoAdjunto'] == current_phase]):
                    next_phase_index = next_phase_index - 1
                for phase in ATTACHMENTS_WORKFLOW[next_phase_index:]:
                    self.__process_attachments_by_phase(
                            initiative,
                            [attachment for attachment in attachments
                                if attachment['infoAdjunto'] == phase],
                            phase)
        if 'content' not in initiative:
            initiative['content'] = ['']

    def __process_attachments_by_phase(self, initiative, attachments, phase):
        correct_counter = 0
        full_content = []
        for attachment in attachments:
            response = requests.get(attachment['appURL'])
            if not response.ok:
                continue
            try:
                with tempfile.NamedTemporaryFile(suffix=MIMETYPE_FILE_EXTENSIONS[attachment['tipoArchivo']]) as f:
                    f.write(bytes(response.content))
                    try:
                        content = process(f.name).decode('utf-8').strip()
                        content = content.replace('\n', ' ').replace('\f', ' ').replace('\t', '')
                        content = [x for x in re.split(r'\.(?!\d)', content) if x != '']
                        if len(content):
                            correct_counter = correct_counter + 1
                    except Exception:
                        content = ['']
                    f.close()
            except KeyError:
                pass  # Mimetype not found in our list
                content = ['']
            full_content = full_content + content
        if correct_counter:
            initiative['content'] = full_content
            initiative['extra']['content_reference'] = phase
            initiative['extra']['content_counter'] = len(attachments)

    def __parse_date(self, str_date):
        split_date = str_date.split('/')
        if len(split_date) != 3:
            return None
        return datetime(int(split_date[2]), int(split_date[1]), int(split_date[0]))
