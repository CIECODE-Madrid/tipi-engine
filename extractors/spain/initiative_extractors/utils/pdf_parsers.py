from pdf2image import convert_from_path
from pytesseract import image_to_string
from textract import process

import requests
import tempfile

class PDFParser():
    def __init__(self, file):
        self.file = file

    def extract(self):
        content = process(self.file.name)
        content = content.decode('utf-8').strip()
        content = content.replace('\f', ' ').replace('\t', '').split('\n')
        return content

class PDFImageParser():
    def __init__(self, file):
        self.file = file

    def extract(self):
        images = convert_from_path(self.file.name)
        texts = []

        for i in range(len(images)):
            text = image_to_string(images[i], lang = 'spa')
            texts.append(text)

        return texts

class PDFExtractor():
    BASE_URL = 'https://www.congreso.es'

    def __init__(self, url, is_img=False):
        self.url = self.BASE_URL + url
        self.is_img = is_img

    def retrieve(self):
        response = requests.get(self.url)
        content = ''
        if not response.ok:
            return content
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf') as file:
                file.write(bytes(response.content))
                content = self.extract(file, self.is_img)
                file.close()
        except KeyError as e:
            print(e)
            pass
        return content

    def extract(self, pdf, is_img = False):
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
