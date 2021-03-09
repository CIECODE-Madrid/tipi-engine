import os
import luigi
from importlib import import_module as im

from extractors.config import MODULE_EXTRACTOR
from utils import FILES


class ExtractorTask(luigi.Task):
    task_namespace = 'extractors'

    def output(self):
        return luigi.LocalTarget(FILES[0])

    def run(self):
        print("{task}(says: ready to extract data!".format(task=self.__class__.__name__))
        members = im('extractors.{}.members'.format(MODULE_EXTRACTOR))
        members.MembersExtractor().extract()
        initiatives = im('extractors.{}.initiatives'.format(MODULE_EXTRACTOR))
        initiatives.InitiativesExtractor().extract()

        self.output().open('w').close()
