import re
import time
from datetime import datetime
from logger import get_logger

from bs4 import BeautifulSoup

from tipi_data.models.initiative import Initiative
from tipi_data.utils import generate_id

from .initiative_status import has_finished


log = get_logger(__name__)

class InitiativeExtractor:
    def __init__(self, response):
        self.initiative = Initiative()
        self.url = response.url
        self.soup = BeautifulSoup(response.text, 'lxml')
        self.reference_regex = r'\([0-9]{3}/[0-9]{6}\)'
        self.date_regex = r'[0-9]{2}/[0-9]{2}/[0-9]{4}'

    def extract(self):
        full_title = self.soup.select_one('.entradilla-iniciativa').text
        self.initiative['title'] = re.sub(self.reference_regex, '', full_title).strip()
        self.initiative['reference'] = re.search(self.reference_regex, full_title).group().strip().strip('()')
        self.initiative['initiative_type'] = self.initiative['reference'].split('/')[0]
        self.initiative['initiative_type_alt'] = self.soup.select('.titular-seccion')[1].text[:-1]
        # TODO extract place from initiative_type_alt or page or sessions diary
        self.initiative['place'] = None
        self.initiative['author_deputies'] = []
        self.initiative['author_parliamentarygroups'] = []
        self.initiative['author_others'] = []
        self.initiative['created'] = self.__parse_date(re.search(
            self.date_regex,
            self.soup.select_one('.f-present').text.split(',')[0].strip()).group())
        self.initiative['updated'] = self.get_last_date()
        self.initiative['processing'] = self.get_processing()
        self.initiative['status'] = None
        self.initiative['url'] = self.url
        self.initiative['id'] = generate_id(
                self.initiative['reference'],
                u''.join(self.initiative['author_deputies']),
                u''.join(self.initiative['author_parliamentarygroups']),
                u''.join(self.initiative['author_others']))
        self.initiative.save()
        log.warning(f"Iniciativa {self.initiative['reference']} procesada")

    def get_last_date(self):
        all_dates = re.findall(self.date_regex, self.soup.select_one('#portlet_iniciativas').text.strip())
        all_dates.sort(key=lambda d: time.mktime(time.strptime(d, "%d/%m/%Y")), reverse=True)
        return self.__parse_date([
            d
            for d in all_dates
            if time.mktime(time.strptime(d, "%d/%m/%Y")) < time.time()
            ][0])

    def get_processing(self):
        current_processing = self.soup.select_one('.situacionActual')
        if current_processing:
            return current_processing.text
        final_processing = self.soup.select_one('.resultadoTramitacion')
        if final_processing:
            return final_processing.text
        return ''

    def __parse_date(self, str_date):
        split_date = str_date.split('/')
        if len(split_date) != 3:
            return None
        return datetime(int(split_date[2]), int(split_date[1]), int(split_date[0]))

    # def __untag(self, initiative):
    #     initiative['topics'] = []
    #     initiative['tags'] = []
    #     initiative['tagged'] = False

