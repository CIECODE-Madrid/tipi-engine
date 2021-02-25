import re
from lxml.html import document_fromstring

import requests

from logger import get_logger
from .initiative_extractor import InitiativeExtractor


log = get_logger(__name__)

class BulletinsExtractor(InitiativeExtractor):
    LETTER = 'Z'
    TAG_RE = re.compile(r'<[^>]+>') # TODO Move to utils

    def extract_content(self):
        self.initiative['content'] = self.retrieve_bulletin()

    def retrieve_bulletin(self):
        content = list()
        try:
            for url in self.find_urls():
                bulletin_tree = document_fromstring(requests.get(
                    f"{self.BASE_URL}{url}"
                    ).text)
                bulletin_content = bulletin_tree.cssselect('.textoIntegro')
                if bulletin_content:
                    content += [line for line in list(map(
                        lambda x: self.TAG_RE.sub('', x).strip(),
                        bulletin_content[0].itertext()
                        )) if line != '']
            return content
        except IndexError:
            # log.error(f"Index error on getting bulletin on initiative {self.url}")
            return list()
        except Exception as e:
            # log.error(f"Error getting content bulletin on initiative {self.url}")
            log.error(e)
            return list()

    def find_urls(self):
        return self.node_tree.xpath(self.get_xpath())

    def get_xpath(self):
        return f"//ul[@class='boletines']/li/div[contains(text(),'{self.LETTER}-')]/following-sibling::div/a[1]/@href"


class ABulletinsExtractor(BulletinsExtractor):
    LETTER = 'A'


class BBulletinsExtractor(BulletinsExtractor):
    LETTER = 'B'


class CBulletinsExtractor(BulletinsExtractor):
    LETTER = 'C'


class DBulletinsExtractor(BulletinsExtractor):
    LETTER = 'D'


class EBulletinsExtractor(BulletinsExtractor):
    LETTER = 'E'


class FirstBulletinExtractor(BulletinsExtractor):
    LETTER = 'Z'

    def get_xpath(self):
        return f"//ul[@class='boletines']/li/div[contains(text(),'{self.LETTER}-')]/following-sibling::div[1]/a[1]/@href"


class FirstABulletinExtractor(FirstBulletinExtractor):
    LETTER = 'A'


class FirstBBulletinExtractor(FirstBulletinExtractor):
    LETTER = 'B'


class FirstCBulletinExtractor(FirstBulletinExtractor):
    LETTER = 'C'


class FirstDBulletinExtractor(FirstBulletinExtractor):
    LETTER = 'D'


class FirstEBulletinExtractor(FirstBulletinExtractor):
    LETTER = 'E'
