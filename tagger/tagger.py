import luigi

from targets import *
from utils import FILES
from data_cleaners.transformations import TransformationsTask
from .tag_initiatives import TagInitiatives


class TaggerTask(luigi.Task):
    task_namespace = 'tagger'

    def requires(self):
        return TransformationsTask()

    def output(self):
        return luigi.LocalTarget(FILES[2])

    def run(self):
        print("{task} says: ready to tag initiatives!".format(task=self.__class__.__name__))
        TagInitiatives().run()
        self.output().open('w').close()
