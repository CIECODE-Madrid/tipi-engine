import luigi

from search import NotifyByEmail
from labeling.labeling import LabelingTask
from targets import *
from utils import FILES


class GenerateAlertsTask(luigi.Task):
    task_namespace = 'alerts'

    def requires(self):
        return LabelingTask()

    def output(self):
        return luigi.LocalTarget(FILES[3])

    def run(self):
        print("{task} says: ready to generate alerts!".format(task=self.__class__.__name__))
        NotifyByEmail()
        self.output().open('w').close()
