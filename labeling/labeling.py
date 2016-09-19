import luigi
from scraper.scraper import ScrapTask
from targets import *
from utils import FILES
from labeling.motor_pcre import LabelingEngine

class LabelingTask(luigi.Task):
    task_namespace = 'labeling'

    def requires(self):
        return ScrapTask()

    def output(self):
        return luigi.LocalTarget(FILES[1])

    def run(self):
        print("{task} says: ready to search and assign labels!".format(task=self.__class__.__name__))
        labeling_engine = LabelingEngine()
        labeling_engine.run()
        self.output().open('w').close()
