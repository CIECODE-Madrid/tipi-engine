import re
import html
import requests

from lxml.html import document_fromstring, tostring

from .initiative_extractor import InitiativeExtractor

from logger import get_logger



class BulletinsExtractor(InitiativeExtractor):
    LETTER = 'Z'
    TAG_RE = re.compile(r'<[^>]+>')  # TODO Move to utils

    def extract_content(self):
        if not self.has('content'):
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
            return list()
        except Exception as e:
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


class NonExclusiveBulletinExtractor(InitiativeExtractor):
    BASE_URL = 'https://www.congreso.es'
    PAGE_FIND_REGEX = 'Pág.:\s([0-9]+)'
    HTML_STRIP_REGEX = '<[^>]+>'

    def extract_content(self):
        self.initiative['content'] = self.extract_bulletin_content()

    def extract_bulletin_metadata(self):
        text = self.node_tree.xpath("//ul[@class='boletines']/li[1]/div[1]")[0].text_content()
        link = self.node_tree.xpath("//ul[@class='boletines']/li[1]/div[2]/a[1]/@href")[0]

        self.page = re.search(self.PAGE_FIND_REGEX, text).group(1)
        self.link = self.BASE_URL + link

    def extract_bulletin_content(self):
        try:
            self.extract_bulletin_metadata()
        except Exception:
            # No Bulletin yet
            self.initiative['status'] = 'En tramitación'
            return []

        tree = document_fromstring(requests.get(self.link).text)

        try:
            element = tree.xpath("//div[contains(@class, 'textoIntegro')]")[0]
        except Exception:
            # Bulletin not properly formatted
            self.initiative['status'] = 'En tramitación'
            return []

        full_content = str(tostring(element))
        full_content = full_content.replace('<br><br><br><br>', "\n").replace('<br><br><br>', "\n").replace('<br>', " ")
        full_content = re.sub(self.HTML_STRIP_REGEX, '', full_content)
        full_content = html.unescape(full_content)

        clean_content = self.clean_str_to_substr(full_content, 'Página ' + self.page)
        clean_content = self.clean_str_to_substr(clean_content, self.initiative['reference'])

        try:
            end_pos = re.search('[0-9]{3}/[0-9]{6}', clean_content).start()
        except Exception:
            # Last initiative in the Bulletin.
            return clean_content.split("\n")

        content = clean_content[:end_pos]
        return content.split("\n")

    def clean_str_to_substr(self, haystack, needle):
        pos = haystack.find(needle) + len(needle)
        return haystack[pos:]
