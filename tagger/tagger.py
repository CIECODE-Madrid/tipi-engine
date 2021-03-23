import luigi

from targets import *
from utils import FILES
from extractors.extractor import ExtractorTask
from .tag_initiatives import TagInitiatives


class TaggerTask(luigi.Task):
    task_namespace = 'tagger'

    def requires(self):
        return ExtractorTask()

    def output(self):
        return luigi.LocalTarget(FILES[1])

    def run(self):
        print("{task} says: ready to tag initiatives!".format(task=self.__class__.__name__))
        TagInitiatives().run()
        self.output().open('w').close()
