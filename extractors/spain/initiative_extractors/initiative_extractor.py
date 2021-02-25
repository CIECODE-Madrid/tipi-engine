import re
import time
from datetime import datetime
from lxml.html import document_fromstring

from bs4 import BeautifulSoup

from tipi_data.models.initiative import Initiative
from tipi_data.utils import generate_id

from logger import get_logger
from .initiative_status import has_finished


log = get_logger(__name__)


class InitiativeExtractor:
    def __init__(self, response, deputies, parliamentarygroups, places):
        self.node_tree = document_fromstring(response.text)
        self.initiative = Initiative()
        self.deputies = deputies
        self.parliamentarygroups = parliamentarygroups
        self.places = places
        self.url = response.url
        self.soup = BeautifulSoup(response.text, 'lxml')
        self.reference_regex = r'\([0-9]{3}/[0-9]{6}\)'
        self.date_regex = r'[0-9]{2}/[0-9]{2}/[0-9]{4}'
        self.parliamentarygroup_sufix = r' en el Congreso'

    def extract(self):
        self.extract_commons()
        self.extract_content()
        self.initiative.save()

    def extract_content(self):
        self.initiative['content'] = []

    def extract_commons(self):
        try:
            # TODO get source initiative
            full_title = self.soup.select_one('.entradilla-iniciativa').text
            self.initiative['title'] = re.sub(self.reference_regex, '', full_title).strip()
            self.initiative['reference'] = re.search(self.reference_regex, full_title).group().strip().strip('()')
            self.initiative['initiative_type'] = self.initiative['reference'].split('/')[0]
            self.initiative['initiative_type_alt'] = self.soup.select('.titular-seccion')[1].text[:-1]
            self.initiative['place'] = self.get_place()
            self.populate_authors()
            self.initiative['created'] = self.__parse_date(re.search(
                self.date_regex,
                self.soup.select_one('.f-present').text.split(',')[0].strip()).group())
            self.initiative['updated'] = self.get_last_date()
            self.initiative['history'] = self.get_history()
            if 'extra' not in self.initiative or self.initiative.extra == {}:
                self.initiative['extra'] = dict()
            self.initiative['extra']['latest_history_item'] = self.initiative['history'][-1] \
                if len(self.initiative['history']) \
                else ''
            self.initiative['url'] = self.url
            self.initiative['id'] = self.generate_id(self.initiative)
            log.info(f"Iniciativa {self.initiative['reference']} procesada")
        except AttributeError:
            log.error(f"Error processing some attributes for initiative {self.url}")
            log.error(str(e))
        except Exception as e:
            log.error(f"Error processing initiative {self.url}")
            log.error(str(e))

    def generate_id(self, initiative):
        return generate_id(
                    initiative['reference'],
                    u''.join(initiative['author_deputies']),
                    u''.join(initiative['author_parliamentarygroups']),
                    u''.join(initiative['author_others']))

    def get_last_date(self):
        try:
            all_dates = re.findall(self.date_regex, self.soup.select_one('#portlet_iniciativas').text.strip())
            all_dates.sort(key=lambda d: time.mktime(time.strptime(d, "%d/%m/%Y")), reverse=True)
            return self.__parse_date([
                d
                for d in all_dates
                if time.mktime(time.strptime(d, "%d/%m/%Y")) < time.time()
                ][0])
        except Exception:
            return None

    def populate_authors(self):
        self.initiative['author_deputies'] = []
        self.initiative['author_parliamentarygroups'] = []
        self.initiative['author_others'] = []
        xpath = "//section[@id='portlet_iniciativas']//div[@class=' portlet-content-container']//h3[contains(text(),'Autor')]/following-sibling::ul[1]/li"
        authors_list = self.node_tree.xpath(xpath)

        for item in authors_list:
            a_tags = item.cssselect('a')
            if len(a_tags) == 0:
                self.initiative['author_others'].append(item.text_content())
            else:
                regex_short_parliamentarygroup = r' \(.+\)'
                regex_more_deputies = r' y [0-9]+ Diputados'
                has_short_parliamentarygroup = re.search(regex_short_parliamentarygroup, item.text_content())
                if has_short_parliamentarygroup:
                    deputy_name = re.sub(regex_short_parliamentarygroup, '', item.text_content())
                    if re.search(regex_more_deputies, deputy_name):
                        deputy_name = re.sub(regex_more_deputies, '', deputy_name)
                        self.initiative['author_others'].append(item.text_content())
                    if self.__is_deputy(deputy_name):
                        self.initiative['author_deputies'].append(deputy_name)
                        parliamentarygroup_name = self.__get_parliamentarygroup_name(
                                has_short_parliamentarygroup.group()[2:][:-1])
                        if parliamentarygroup_name:
                            self.initiative['author_parliamentarygroups'].append(parliamentarygroup_name)
                else:
                    parliamentarygroup_name = item.text_content() \
                        if self.parliamentarygroup_sufix not in item.text_content() \
                        else re.sub(self.parliamentarygroup_sufix, '', item.text_content())
                    self.initiative['author_parliamentarygroups'].append(parliamentarygroup_name)

    def get_place(self):
        place = ''
        try:
            place_wrapper = self.soup.select_one('.comisionesCompetentes')
            if place_wrapper:
                place = place_wrapper.text.strip()
            else:
                history = self.get_history()
                for place in self.places:
                    for history_item in history:
                        if place['name'] in history_item:
                            place = place['name']
                            break
        except Exception as e:
            pass
        return place

    def get_history(self):
        history = list()
        try:
            history_wrapper = self.soup.select_one('.iniciativaTramitacion')
            if history_wrapper:
                TAG_RE = re.compile(r'<[^>]+>')
                history = list(map(
                    lambda x: TAG_RE.sub('', x).strip(),
                    str(history_wrapper).split('<br/>')
                    ))
                final_status_wrapper = self.soup.select_one('.resultadoTramitacion')
                if final_status_wrapper:
                    history.append(final_status_wrapper.text)
        except Exception:
            pass
        return history

    def __is_deputy(self, name):
        for deputy in self.deputies:
            if deputy.name == name:
                return True
        return False

    def __is_parliamentarygroup(self, name):
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
