import luigi
from importlib import import_module as im

from extractors.config import MODULE_EXTRACTOR
from utils import FILES


class ExtractorTask(luigi.Task):
    task_namespace = 'extractors'

    def __init__(self):
        self.members_extractor = im('extractors.{}.members'.format(MODULE_EXTRACTOR)).MembersExtractor()
        self.initiatives_extractor = im('extractors.{}.initiatives'.format(MODULE_EXTRACTOR)).InitiativesExtractor()
        super().__init__()

    def output(self):
        return luigi.LocalTarget(FILES[0])

    def run(self):
        print("{task}(says: ready to extract data!".format(task=self.__class__.__name__))
        self.members()
        self.initiatives()
        self.end()

    def members(self):
        self.members_extractor.extract()

    def initiatives(self):
        self.initiatives_extractor.extract()

    def references(self):
        self.initiatives_extractor.extract_references()
        print(self.initiatives_extractor.all_references)

    def end(self):
        self.output().open('w').close()
