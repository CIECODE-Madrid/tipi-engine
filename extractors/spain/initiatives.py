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
from tipi_data.models.initiative import Initiative

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
        initiatives = Initiative.all.order_by('reference').only('reference')

        last_references = {}
        totals = {}
        previous_ref = 1

        for initiative in initiatives:
            items = initiative['reference'].split('/')
            initiative_type = items[0]
            reference = items[1]

            if initiative_type not in totals:
                totals[initiative_type] = 0

            last_references[initiative_type] = reference
            int_reference = int(reference)
            self.all_references += self.calculate_references_between(previous_ref, int_reference, initiative_type)

            totals[initiative_type] += 1
            previous_ref = int_reference + 1

        for initiative_type in self.INITIATIVE_TYPES:
            code = initiative_type['code']
            title = initiative_type['type']

            db_last_reference = int(last_references[code]) if code in last_references else 0
            origin_total = self.totals_by_type[title] if title in self.totals_by_type else 0
            db_total = totals[code] if code in totals else 0

            new_items = origin_total - db_total
            if not new_items:
                continue

            for extra in range(1, new_items + 3):
                self.all_references.append(self.format_reference(db_last_reference + extra, code))

    def calculate_references_between(self, previous_ref, new_ref, initiative_type):
        missing_references = []
        while previous_ref < new_ref:
            missing_reference = self.format_reference(previous_ref, initiative_type)
            previous_ref += 1
            missing_references.append(missing_reference)

        return missing_references

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

    def format_reference(self, ref, initiative_type):
        reference = str(ref)
        missing_zeros = 6 - len(reference)
        return initiative_type + '/' + ('0' * missing_zeros) + reference
