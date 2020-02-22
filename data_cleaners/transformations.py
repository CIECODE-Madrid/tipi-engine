from importlib import import_module as im

import luigi

from data_cleaners.config import MODULE_DATA_CLEANER as CLEANER
from extractors.scraper import ScrapTask
from utils import FILES

populate_status = im('data_cleaners.{}.populate_status'.format(CLEANER))
convert_urls = im('data_cleaners.{}.convert_urls'.format(CLEANER))


class TransformationsTask(luigi.Task):
    task_namespace = 'data_cleaners'

    def requires(self):
        return ScrapTask()

    def output(self):
        return luigi.LocalTarget(FILES[1])

    def run(self):
        print("{task} says: ready to transform data!".format(task=self.__class__.__name__))
        populate_status.PopulateStatus().populate()
        convert_urls.ConvertURLs().convert()
        self.output().open('w').close()
