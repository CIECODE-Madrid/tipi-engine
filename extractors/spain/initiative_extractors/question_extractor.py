from .initiative_extractor import InitiativeExtractor
from .utils.pdf_parsers import PDFParser, PDFImageParser
from lxml.html import document_fromstring

def QuestionExtractor(InitiativeExtractor):

    QUESTION = 'Pregunta'
    ANSWER = 'Contestación'
    HREF = 'href'
    A = 'a'
    BASE_URL = 'https://www.congreso.es'

    def extract_content(self):
        self.node_tree = document_fromstring(self.response.text)
        # self.initiative['content'] = self.retrieve_question()
        self.initiative['content'] = []

    def retrieve_question(self):
        return self.retrieve_content(self.QUESTION, True)

    def retrieve_answer(self):
        return self.retrieve_content(self.ANSWER)

    def retrieve_content(self, content, is_img = False):
        url = self.BASE_URL + self.find_url(content)
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
        if (is_img):
            pdf_parser = PDFImageParser(pdf)
        else:
            pdf_parser = PDFParser(pdf)

        try:
            content = pdf_parser.extract()

            content = content.decode('utf-8').strip()
            content = content.replace('\n', ' ').replace('\f', ' ').replace('\t', '')
        except Exception as e:
            print(e)
            pass
        return content

    def find_url(self, content):
        items = self.node_tree.xpath(f"//a[contains(., '{content}')]")
        return items[0].get(self.HREF)
