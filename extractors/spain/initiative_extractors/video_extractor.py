import requests
import math
from tipi_data.utils import generate_id
from tipi_data.models.video import Video

class VideoExtractor():

    def __init__(self, reference):
        self.reference = reference

    def extract(self):
        json = self.retrieve_json(1)
        if 'error' in json:
            return
        total = int(json['intervenciones_encontradas'])
        pages = math.ceil(total / 25)

        self.extract_interventions(json['lista_intervenciones'])

        if pages > 1:
            for x in range(2, pages):
                json = self.retrieve_json(1)
                self.extract_interventions(json['lista_intervenciones'])

    def extract_interventions(self, interventions):
        for intervention_key in interventions:
            json = interventions[intervention_key]

            video = Video()
            video['link'] = json['video_intervencion']['enlace_descarga02']
            video['id'] = self.generate_id(video['link'])
            video['reference'] = self.reference
            video['date'] = json['fecha']
            video['session_name'] = json['sesion']['nombre_sesion']

            if 'tipo_intervencion' in json:
                video['type'] = json['tipo_intervencion']
            if 'orador' in json:
                video['speaker'] = json['orador']

            video.save()


    def retrieve_json(self, page):
        url = 'https://www.congreso.es/web/guest/busqueda-de-intervenciones?p_p_id=intervenciones&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=filtrarListado&p_p_cacheability=cacheLevelPage&_intervenciones_mode=view&_intervenciones_legislatura=XIV&_intervenciones_id_iniciativa=' + self.reference
        data = {
            '_intervenciones_paginaActual': page
        }
        response = requests.post(url, data=data)
        return response.json()

    def generate_id(self, link):
        return generate_id(link)
