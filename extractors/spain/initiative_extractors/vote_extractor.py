from lxml.html import document_fromstring
from lxml.etree import tostring
from html import unescape
from tipi_data.models.voting import Voting
from logger import get_logger
from tipi_data.utils import generate_id
import re
import requests

log = get_logger(__name__)

class VoteExtractor():
    JSON_XPATH = "//div[@class='votaciones']/div[1]/a[contains(text(), 'JSON')]"
    VOTE_TYPES = [
        'Toma en consideración',
        'Debate de totalidad',
        'Votación de conjunto'
    ]

    def __init__(self, tree, initiative):
        self.tree = tree
        self.initiative = initiative

    def extract(self):
        votes_html = self.get_votes_html()
        for item in votes_html:
            for type in self.VOTE_TYPES:
                if type in item:
                    link = self.extract_link(item)
                    self.extract_votes(link)

    def get_votes_html(self):
        elements = self.tree.cssselect('.votaciones')
        if len(elements) == 0:
            return []
        element = elements[0]
        html_string = tostring(element).decode('utf-8').replace('&#13;', '')
        html = html_string[24:].strip()
        return self.split_html(html)

    def split_html(self, html):
        items = html.split('JSON</a>')
        cleaned = []
        for item in items:
            cleaned.append(unescape(item)+ 'JSON</a>')

        return cleaned[:len(cleaned) - 1]

    def extract_link(self, html):
        regex = re.compile('<a[\sa-zA-Z\"\.=0-9_\/:]+\>JSON\<\/a\>')
        matches = regex.findall(html)
        tag = matches[0]
        start = tag.find('href="') + 6
        link = tag[start:]
        end = link.find('"')
        return link[:end]

    def extract_votes(self, url):
        response = requests.get(url)
        data = response.json()
        self.save_votes(data)

    def get_party_votes(self, data):
        votaciones = data.get('votaciones')
        party_votes = {}
        for vote in votaciones:
            group = vote.get('grupo')
            vote_value = vote.get('voto')

            if group not in party_votes:
                party_votes[group] = {}
            if vote_value not in party_votes[group]:
                party_votes[group][vote_value] = 0

            party_votes[group][vote_value] = party_votes[group][vote_value] + 1

        return party_votes

    def vote_exists(self):
        return False
        # return Voting.objects(id=self.initiative['id'])

    def save_votes(self, data):
        votes = Voting()
        information = data.get('informacion')
        votes['id'] = self.generate_id(self.initiative['reference'], information.get('tituloSubGrupo'))
        votes['reference'] = self.initiative['reference']
        votes['title'] = information.get('textoExpediente')
        votes['subgroup_text'] = information.get('textoSubGrupo')
        votes['subgroup_title'] = information.get('tituloSubGrupo')

        totals = data.get('totales')
        votes['total_yes'] = totals.get('afavor')
        votes['total_no'] = totals.get('enContra')
        votes['total_abstention'] = totals.get('abstenciones')
        votes['total_skip'] = totals.get('noVotan')
        votes['total_present'] = totals.get('presentes')

        votes['by_party'] = self.get_party_votes(data)
        votes['by_deputy'] = data.get('votaciones')

        votes.save()

    def generate_id(self, reference, text):
        return generate_id(
            reference,
            text
        )


