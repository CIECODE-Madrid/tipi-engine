import os
import luigi
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess, Crawler



#from scraper.scrap.scrap.spiders.initiatives import InitiativesSpider
from targets import *
from utils import FILES


class ScrapTask(luigi.Task):
    task_namespace = 'scraper'

    def output(self):
        return luigi.LocalTarget(FILES[0])

    def run(self):
        print("{task} says: ready to scrap!".format(task=self.__class__.__name__))
        #execfile("scraper/scrap/scrap/initiatives.py")

        os.chdir("scraper/scrap/scrap")
        os.system("python members.py")
        os.system("python initiatives.py")
        os.chdir("../../../")

        self.output().open('w').close()
