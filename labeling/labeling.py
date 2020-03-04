import luigi

from targets import *
from utils import FILES
from data_cleaners.transformations import TransformationsTask
from .motor_pcre import LabelingEngine


class LabelingTask(luigi.Task):
    task_namespace = 'labeling'

    def requires(self):
        return TransformationsTask()

    def output(self):
        return luigi.LocalTarget(FILES[2])

    def run(self):
        print("{task} says: ready to search and assign labels!".format(task=self.__class__.__name__))
        labeling_engine = LabelingEngine()
        labeling_engine.run()
        self.output().open('w').close()
