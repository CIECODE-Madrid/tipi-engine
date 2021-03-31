from lxml.html import document_fromstring
import requests
from tipi_data.models.voting import Voting
from logger import get_logger

log = get_logger(__name__)

class VoteExtractor():
    JSON_XPATH = "//div[@class='votaciones']/div[1]/a[contains(text(), 'JSON')]"

    def __init__(self, tree, initiative):
        self.tree = tree
        self.initiative = initiative
        self.json_url = self.get_json_link()

    def extract(self):
        if self.vote_exists():
            return
        response = requests.get(self.json_url)
        data = response.json()
        self.save_votes(data)

    def get_json_link(self):
        elements = self.tree.xpath(self.JSON_XPATH)
        element = elements[0]
        return element.get('href')

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
        return Voting.objects(id=self.initiative['id'])

    def save_votes(self, data):
        votes = Voting()
        votes['id'] = self.initiative['id']
        votes['reference'] = self.initiative['reference']
        votes['title'] = data.get('informacion').get('textoExpediente')

        totals = data.get('totales')
        votes['total_yes'] = totals.get('afavor')
        votes['total_no'] = totals.get('enContra')
        votes['total_abstention'] = totals.get('abstenciones')
        votes['total_skip'] = totals.get('noVotan')
        votes['total_present'] = totals.get('presentes')

        votes['by_party'] = self.get_party_votes(data)
        votes['by_deputy'] = data.get('votaciones')

        votes.save()

