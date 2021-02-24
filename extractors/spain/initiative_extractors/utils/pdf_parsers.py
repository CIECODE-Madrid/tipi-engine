from pdf2image import convert_from_path
from pytesseract import image_to_string
from textract import process

class PDFParser():
    def __init__(self, file):
        self.file = file

    def extract(self):
        content = process(self.file.name)
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

        return ' '.join(texts)
