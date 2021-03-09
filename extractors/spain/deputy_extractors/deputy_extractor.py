import re
from lxml.html import document_fromstring
from tipi_data.models.deputy import Deputy
from urllib.parse import urlparse, parse_qs

class DeputyExtractor():
    def __init__(self, response):
        self.response = response
        self.node_tree = document_fromstring(response.text)
        self.deputy = Deputy()

    def extract(self):
        self.deputy['name'] = self.get_text_by_css('.nombre-dip')
        self.deputy['parliamentarygroup'] = self.get_text_by_css('.grupo-dip a')
        self.deputy['image'] = self.get_src_by_css('.img-dip img')
        self.deputy['email'] = self.get_text_by_css('.email-dip a')
        self.deputy['public_position'] = self.get_public_positions()
        self.deputy['party_logo'] = self.get_src_by_css('.logo-partido img')
        self.deputy['url'] = self.response.url
        self.deputy['constituency'] = self.get_text_by_css('.cargo-dip').replace("Diputado por", "")

        self.extract_id()
        self.extract_social_media()
        self.extract_extras()
        self.extract_dates()
        self.extract_from_text()
        self.deputy.save()

    def get_src_by_css(self, selector):
        item = self.get_by_css(selector)
        if len(item) == 0:
            return ''

        return self.clean_str(item[0].get('src'))

    def get_text_by_css(self, selector):
        item = self.get_by_css(selector)
        if len(item) == 0:
            return ''

        return self.clean_str(item[0].text)


    def get_by_css(self, selector):
        return self.node_tree.cssselect(selector)

    def get_by_xpath(self, xpath):
        return self.node_tree.xpath(xpath)

    def extract_id(self):
        url = urlparse(self.response.url)
        query = parse_qs(url[4])
        self.deputy['id'] = query['codParlamentario'][0]

    def clean_str(self, string):
        return re.sub('\s+', ' ', string).strip()

    def get_public_positions(self):
        positions = []
        for position in self.get_by_css('.cargos:not(.ult-init) li'):
            positions.append(self.clean_str(position.text_content()))
        return positions

    def extract_dates(self):
        date_elements = self.get_by_css('.f-alta')
        end_date = self.clean_str(date_elements[1].text_content()).replace("Causó baja el ", "")
        pos = end_date.find(' Sustituido')

        self.deputy['start_date'] = self.clean_str(date_elements[0].text_content()).replace("Condición plena: ", "")
        self.deputy['end_date'] = end_date[:pos]
        self.deputy['active'] = end_date[:pos] == ''

    def extract_social_media(self):
        social_links = self.get_by_css('.rrss-dip a')
        for link in social_links:
            img_src = link.getchildren()[0].get('src')
            if 'twitter' in img_src:
                self.deputy['twitter'] = link.get('href')
            if 'facebook' in img_src:
                self.deputy['facebook'] = link.get('href')
            if 'web' in img_src:
                self.deputy['web'] = link.get('href')

    def extract_extras(self):
        self.deputy['extra'] = []
        links = self.get_by_css('.declaraciones-dip a')
        for link in links:
            self.deputy['extra'].append(('https://www.congreso.es' + link.get('href'), self.clean_str(link.text)))

    def extract_from_text(self):
        birthday_paragraph = self.clean_str(self.get_by_xpath("//h3[normalize-space(text()) = 'Ficha personal']/following-sibling::p[1]")[0].text)
        self.deputy['birthdate'] = birthday_paragraph.replace("Nacido el ", "")

        legislatures_paragraph = self.clean_str(self.get_by_xpath("//h3[normalize-space(text()) = 'Ficha personal']/following-sibling::p[2]")[0].text)
        self.deputy['legislatures'] = legislatures_paragraph.replace("Diputado de la ", "").replace(" Legislaturas", "").replace("y ", "").split(", ")

        bio = self.clean_str(self.get_by_xpath("//h3[normalize-space(text()) = 'Ficha personal']/parent::div")[0].text_content())
        bio = bio.replace("Ficha personal", "").replace(birthday_paragraph, "").replace(legislatures_paragraph, "")
        pos = bio.find(' Condición plena')
        self.deputy['bio'] = self.clean_str(bio[:pos]).split('. ')
