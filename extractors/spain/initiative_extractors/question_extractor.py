from .initiative_extractor import InitiativeExtractor
from .utils.pdf_parsers import PDFParser, PDFImageParser
from lxml.html import document_fromstring
from copy import deepcopy
import requests
import tempfile

class QuestionExtractor(InitiativeExtractor):

    QUESTION = 'Pregunta'
    ANSWER = 'Contestación'
    HREF = 'href'
    A = 'a'
    BASE_URL = 'https://www.congreso.es'

    def extract_content(self):
        self.node_tree = document_fromstring(self.response.text)
        self.initiative['content'] = self.retrieve_question()
        self.create_answer_initative(self.retrieve_answer())

    def create_answer_initative(self, answer):
        if answer == '':
            return
        answer_initiative = deepcopy(self.initiative)
        answer_initiative['content'] = answer
        answer_initiative['initiative_type_alt'] = 'Respuesta'
        answer_initiative['author_others'] = ['Gobierno']
        answer_initiative['author_deputies'] = []
        answer_initiative['author_parliamentarygroups'] = []
        answer_initiative['id'] = self.generate_id(answer_initiative)
        answer_initiative.save()

    def retrieve_question(self):
        return self.retrieve_content(self.QUESTION, True)

    def retrieve_answer(self):
        return self.retrieve_content(self.ANSWER)

    def retrieve_content(self, content, is_img = False):
        try:
            url = self.BASE_URL + self.find_url(content)
        except Exception:
            # URL not found, do not download the PDF.
            return ''
        content = self.download_pdf(url, is_img)
        return content

    def download_pdf(self, url, is_img):
        response = requests.get(url)
        content = ''
        if not response.ok:
            return content
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf') as file:
                file.write(bytes(response.content))
                content = self.extract_pdf(file, is_img)
                file.close()
        except KeyError as e:
            print(e)
            pass
        return content

    def extract_pdf(self, pdf, is_img = False):
        content = ''
        if is_img:
            parser = PDFImageParser(pdf)
        else:
            parser = PDFParser(pdf)

        try:
            content = parser.extract()

        except Exception as e:
            print(e)
            pass
        return content

    def find_url(self, content):
        items = self.node_tree.xpath(f"//a[normalize-space(text()) = '{content}']")
        if len(items) < 0:
            raise Exception('Link not found')
        return items[0].get(self.HREF)
