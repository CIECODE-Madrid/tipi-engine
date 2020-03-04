from importlib import import_module as im

import luigi

from data_cleaners.config import MODULE_DATA_CLEANER as CLEANER
from extractors.extractor import ExtractorTask
from utils import FILES


populate_status = im('data_cleaners.{}.populate_status'.format(CLEANER))
convert_urls = im('data_cleaners.{}.convert_urls'.format(CLEANER))


def run_cleaner():
    populate_status.PopulateStatus().populate()
    convert_urls.ConvertURLs().convert()


class TransformationsTask(luigi.Task):
    task_namespace = 'data_cleaners'

    def requires(self):
        return ExtractorTask()

    def output(self):
        return luigi.LocalTarget(FILES[1])

    def run(self):
        print("{task} says: ready to transform data!".format(task=self.__class__.__name__))
        run_cleaner()
        self.output().open('w').close()
