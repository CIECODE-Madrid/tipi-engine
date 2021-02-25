import re
from lxml.html import document_fromstring

import requests

from logger import get_logger
from .initiative_extractor import InitiativeExtractor


log = get_logger(__name__)


class OneBulletinExtractor(InitiativeExtractor):

    TAG_RE = re.compile(r'<[^>]+>')
    BASE_URL = 'https://www.congreso.es'

    def extract_content(self):
        self.initiative['content'] = self.retrieve_bulletin()

    def get_letter(self):
        pass

    def retrieve_bulletin(self):
        EMPTY = list()
        try:
            bulletins = [
                    li
                    for li in self.node_tree.cssselect('ul.boletines > li')
                    if f'{self.get_letter()}-' in li.text_content()]
            if len(bulletins) == 0:
                return EMPTY
            bulletin_url = f"{self.BASE_URL}{bulletins[0].xpath('div[2]/a[1]/@href')[0]}"
            if not bulletin_url:
                return EMPTY
            bulletin_tree = document_fromstring(requests.get(bulletin_url).text)
            bulletin_content = bulletin_tree.cssselect('.textoIntegro')
            if not bulletin_content:
                return EMPTY
            return [line for line in list(map(
                lambda x: self.TAG_RE.sub('', x).strip(),
                bulletin_content[0].itertext()
                )) if line != '']
        except IndexError:
            log.error(f"Index error on getting bulletin on initiative {self.url}")
            return EMPTY
        except Exception:
            log.error(f"Error getting content bulletin on initiative {self.url}")
            return EMPTY


class OneABulletinExtractor(OneBulletinExtractor):
    def get_letter(self):
        return 'A'


class OneBBulletinExtractor(OneBulletinExtractor):
    def get_letter(self):
        return 'B'


class OneDBulletinExtractor(OneBulletinExtractor):
    def get_letter(self):
        return 'D'


class OneEBulletinExtractor(OneBulletinExtractor):
    def get_letter(self):
        return 'E'
