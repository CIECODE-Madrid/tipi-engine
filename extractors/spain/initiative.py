import re
import time
from datetime import datetime

from bs4 import BeautifulSoup

from tipi_data.models.initiative import Initiative
from tipi_data.models.deputy import Deputy
from tipi_data.models.parliamentarygroup import ParliamentaryGroup
from tipi_data.utils import generate_id

from logger import get_logger
from .initiative_status import has_finished


log = get_logger(__name__)

class InitiativeExtractor:
    def __init__(self, response):
        self.initiative = Initiative()
        self.url = response.url
        self.soup = BeautifulSoup(response.text, 'lxml')
        self.reference_regex = r'\([0-9]{3}/[0-9]{6}\)'
        self.date_regex = r'[0-9]{2}/[0-9]{2}/[0-9]{4}'
        self.parliamentarygroup_sufix = r' en el Congreso'
        self.deputies = Deputy.objects()
        self.parliamentarygroups = ParliamentaryGroup.objects()

    def extract(self):
        try:
            full_title = self.soup.select_one('.entradilla-iniciativa').text
            self.initiative['title'] = re.sub(self.reference_regex, '', full_title).strip()
            self.initiative['reference'] = re.search(self.reference_regex, full_title).group().strip().strip('()')
            self.initiative['initiative_type'] = self.initiative['reference'].split('/')[0]
            self.initiative['initiative_type_alt'] = self.soup.select('.titular-seccion')[1].text[:-1]
            # TODO extract place from initiative_type_alt or page or sessions diary
            self.initiative['place'] = None
            # TODO get source initiative
            self.populate_authors()
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
        except AttributeError:
            log.error(f"Error processing initiative {self.url}")

    def get_last_date(self):
        all_dates = re.findall(self.date_regex, self.soup.select_one('#portlet_iniciativas').text.strip())
        all_dates.sort(key=lambda d: time.mktime(time.strptime(d, "%d/%m/%Y")), reverse=True)
        return self.__parse_date([
            d
            for d in all_dates
            if time.mktime(time.strptime(d, "%d/%m/%Y")) < time.time()
            ][0])

    def populate_authors(self):
        self.initiative['author_deputies'] = []
        self.initiative['author_parliamentarygroups'] = []
        self.initiative['author_others'] = []
        authors_list = self.soup.select_one("""#portlet_iniciativas > div >
                div.portlet-content-container > div > div > div > div >
                div > ul:nth-child(5)""").select('li')
        for item in authors_list:
            if item.select_one('a') is None:
                self.initiative['author_others'].append(item.text)
            else:
                regex_short_parliamentarygroup = r' \(.+\)'
                regex_more_deputies = r' y [0-9]+ Diputados'
                has_short_parliamentarygroup = re.search(regex_short_parliamentarygroup, item.text)
                if has_short_parliamentarygroup:
                    deputy_name = re.sub(regex_short_parliamentarygroup, '', item.text)
                    if re.search(regex_more_deputies, deputy_name):
                        deputy_name = re.sub(regex_more_deputies, '', deputy_name)
                        self.initiative['author_others'].append(item.text)
                    if self.__is_deputy(deputy_name):
                        self.initiative['author_deputies'].append(deputy_name)
                        parliamentarygroup_name = self.__get_parliamentarygroup_name(
                                has_short_parliamentarygroup.group()[2:][:-1])
                        if parliamentarygroup_name:
                            self.initiative['author_parliamentarygroups'].append(parliamentarygroup_name)
                else:
                    parliamentarygroup_name = item.text \
                        if self.parliamentarygroup_sufix not in item.text \
                        else re.sub(self.parliamentarygroup_sufix, '', item.text)
                    self.initiative['author_parliamentarygroups'].append(parliamentarygroup_name)

    def get_processing(self):
        current_processing = self.soup.select_one('.situacionActual')
        if current_processing:
            return current_processing.text
        final_processing = self.soup.select_one('.resultadoTramitacion')
        if final_processing:
            return final_processing.text
        return ''

    def __is_deputy(self, name):
        for deputy in self.deputies:
            if deputy.name == name:
                return True
        return False

    def __is_parliamentarygroup(selg, name):
        for parliamentarygroup in self.parliamentarygroups:
            if parliamentarygroup.name == name:
                return True
        return False

    def __get_parliamentarygroup_name(self, shortname):
        for parliamentarygroup in self.parliamentarygroups:
            if parliamentarygroup.shortname == shortname:
                return parliamentarygroup.name
        return None

    def __parse_date(self, str_date):
        split_date = str_date.split('/')
        if len(split_date) != 3:
            return None
        return datetime(int(split_date[2]), int(split_date[1]), int(split_date[0]))

    # def __untag(self, initiative):
    #     initiative['topics'] = []
    #     initiative['tags'] = []
    #     initiative['tagged'] = False