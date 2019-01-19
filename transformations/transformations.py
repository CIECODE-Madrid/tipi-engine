import luigi
from scraper.scraper import ScrapTask
from targets import *
from utils import FILES
from .populate_status import PopulateStatus
from .convert_urls import ConvertURLs


class TransformationsTask(luigi.Task):
    task_namespace = 'transformations'

    def requires(self):
        return ScrapTask()

    def output(self):
        return luigi.LocalTarget(FILES[1])

    def run(self):
        print("{task} says: ready to transform data!".format(task=self.__class__.__name__))
        PopulateStatus().populate()
        ConvertURLs().convert()
        self.output().open('w').close()
