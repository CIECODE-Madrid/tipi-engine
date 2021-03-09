from .initiative_extractor import InitiativeExtractor
from .utils.pdf_parsers import PDFExtractor
from copy import deepcopy
from .initiative_status import NOT_FINAL_STATUS, ON_PROCESS

class QuestionExtractor(InitiativeExtractor):
    QUESTION = 'Pregunta'
    ANSWER = 'Contestación'
    HREF = 'href'
    A = 'a'

    def extract_content(self):
        self.initiative['content'] = self.retrieve_question()
        answer = self.retrieve_answer()
        if answer == [] and self.initiative['status'] not in NOT_FINAL_STATUS:
            self.initiative['status'] = ON_PROCESS
        else:
            self.create_answer_initative(answer)

    def create_answer_initative(self, answer):
        if answer == []:
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
            url = self.find_url(content)
        except Exception:
            # URL not found, do not download the PDF.
            return []
        extractor = PDFExtractor(url, is_img)
        return extractor.retrieve()

    def find_url(self, content):
        items = self.node_tree.xpath(f"//a[normalize-space(text()) = '{content}']")
        if len(items) < 0:
            raise Exception('Link not found')
        return items[0].get(self.HREF)
