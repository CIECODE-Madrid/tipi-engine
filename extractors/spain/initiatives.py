import json
import time
from math import ceil
from logger import get_logger

import requests
from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed

from tipi_data.models.deputy import Deputy
from tipi_data.models.parliamentarygroup import ParliamentaryGroup
from tipi_data.models.place import Place

from extractors.config import ID_LEGISLATURA
from .initiative_types import INITIATIVE_TYPES
from .initiative_extractor_factory import InitiativeExtractorFactory
from .initiative_extractors.initiative_status import has_finished
from .initiative_extractors.bulletins_extractor import FirstABulletinExtractor
from .utils import int_to_roman


log = get_logger(__name__)


class InitiativesExtractor:

    def __init__(self):
        self.LEGISLATURE = ID_LEGISLATURA
        self.INITIATIVES_PER_PAGE = 25
        self.BASE_URL = 'https://www.congreso.es/web/guest/indice-de-iniciativas'
        self.INITIATIVE_TYPES = INITIATIVE_TYPES
        self.totals_by_type = dict()
        self.all_references = list()
        self.deputies = Deputy.objects()
        self.parliamentarygroups = ParliamentaryGroup.objects()
        self.places = Place.objects()

    def sync_totals(self):
        query_params = {
                'p_p_id': 'iniciativas',
                'p_p_lifecycle': 2,
                'p_p_state': 'normal',
                'p_p_mode': 'view',
                'p_p_resource_id': 'cambiarLegislaturaIndice',
                '_iniciativas_legislatura': self.LEGISLATURE
                }
        response = requests.get(
                self.BASE_URL,
                params=query_params
                )
        soup = BeautifulSoup(response.json()['content'], 'lxml')
        for element in soup.select('.listado_1 li'):
            initiative_type = element.select_one('a').getText().strip()
            if initiative_type[-1] == '.':
                initiative_type = initiative_type[:-1]
            count = int(element.select_one('span').getText().strip('()'))
            self.totals_by_type[initiative_type] = count

    def extract(self):
        start_time = time.time()
        self.extract_references()

        log.info(f"Getting {len(self.all_references)} initiatives references")
        log.debug("--- %s seconds getting references---" % (time.time() - start_time))
        log.info("Processing initiatives...")

        start_time = time.time()
        self.extract_initiatives()
        log.debug("--- %s seconds getting initiatives ---" % (time.time() - start_time))

    def extract_references(self):
        self.sync_totals()
        futures_requests = list()
        session = FuturesSession()
        for initiative_type in self.INITIATIVE_TYPES:
            try:
                END = ceil(self.totals_by_type[initiative_type['type']]/self.INITIATIVES_PER_PAGE)
            except Exception:
                log.warning(f"Unrecognized initiative type: {initiative_type['type']}")
                END = 0
                continue
            query_params = {
                    'p_p_id': 'iniciativas',
                    'p_p_lifecycle': 2,
                    'p_p_state': 'normal',
                    'p_p_mode': 'view',
                    'p_p_resource_id': 'filtrarListado',
                    '_iniciativas_mode': 'verListadoIndice'
                    }
            for page in range(1, END+1):
                form_data = {
                        '_iniciativas_legislatura': self.LEGISLATURE,
                        '_iniciativas_tipo': initiative_type['code'],
                        '_iniciativas_paginaActual': page
                        }
                futures_requests.append(session.post(
                        self.BASE_URL,
                        params=query_params,
                        data=form_data))
        for future in as_completed(futures_requests):
            response = future.result()
            try:
                initiatives = response.json()['lista_iniciativas']
                self.all_references += [
                        initiatives[key]['id_iniciativa']
                        for key in initiatives.keys()
                        if not has_finished(initiatives[key]['id_iniciativa'])]
            except json.decoder.JSONDecodeError:
                log.error(f"Error decoding JSON response on {response.url}")
                continue
            except KeyError:
                log.error(f"Error getting 'lista_iniciativas' on {response.url}")
                continue

    def extract_initiatives(self):
        session = FuturesSession()
        futures_requests = list()
        for reference in self.all_references:
            query_params = {
                    'p_p_id': 'iniciativas',
                    'p_p_lifecycle': 0,
                    'p_p_state': 'normal',
                    'p_p_mode': 'view',
                    '_iniciativas_mode': 'mostrarDetalle',
                    '_iniciativas_legislatura': int_to_roman(ID_LEGISLATURA),
                    '_iniciativas_id': reference
                    }
            futures_requests.append(session.get(
                self.BASE_URL,
                params=query_params))
        for future in as_completed(futures_requests):
            response = future.result()
            if response.ok:
                InitiativeExtractorFactory.create(
                        response,
                        self.deputies,
                        self.parliamentarygroups,
                        self.places
                        ).extract()
