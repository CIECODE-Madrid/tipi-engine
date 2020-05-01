import requests
from datetime import datetime

from tipi_data.utils import generate_id
from tipi_data.models.deputy import Deputy

from .api import ENDPOINT
from .legislative_period import LegislativePeriod


class MembersExtractor:
    def __init__(self):
        self.__legislative_period = LegislativePeriod().get()

    def extract(self):
        response = requests.get(ENDPOINT.format(method='parlamentario'))
        current_members = [p for p in response.json() if p['periodoLegislativo'] == self.__legislative_period]
        for cm in current_members:
            member = Deputy(
                    id=generate_id(str(cm['idParlamentario'])),
                    name="{} {}".format(cm['nombres'], cm['apellidos']).title(),
                    parliamentarygroup=cm['partidoPolitico'],
                    image=cm['fotoURL'],
                    email=None,
                    web=None,
                    twitter=None,
                    start_date=None,
                    end_date=None,
                    url=cm['appURL'],
                    active=True
                    )
            member.save()
