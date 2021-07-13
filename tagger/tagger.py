from utils import FILES
from extractors.extractor import ExtractorTask
from .tag_initiatives import TagInitiatives


class TaggerTask():
    task_namespace = 'tagger'

    def requires(self):
        return ExtractorTask()

    def run(self):
        print("{task} says: ready to tag initiatives!".format(task=self.__class__.__name__))
        TagInitiatives().run()
