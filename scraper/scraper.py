import luigi
from targets import *
from utils import FILES


class ScrapTask(luigi.Task):
    task_namespace = 'scraper'

    def output(self):
        return luigi.LocalTarget(FILES[0])

    def run(self):
        print("{task} says: ready to scrap!".format(task=self.__class__.__name__))
        self.output().open('w').close()
