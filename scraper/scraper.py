from scrapy.utils.project import get_project_settings

from scrapy.crawler import CrawlerProcess, Crawler

import luigi
import pdb



#from scraper.scrap.scrap.spiders.initiatives import InitiativesSpider
from targets import *
from utils import FILES


class ScrapTask(luigi.Task):
    task_namespace = 'scraper'

    def output(self):
        return luigi.LocalTarget(FILES[0])

    def run(self):
        print("{task} says: ready to scrap!".format(task=self.__class__.__name__))
        #execfile("scraper/scrap/scrap/start.py")

        import os
        os.chdir("scraper/scrap/scrap")
        os.system("python start.py")
        os.chdir("../../../")

        self.output().open('w').close()
