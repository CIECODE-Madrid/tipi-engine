from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def extract_members():
    process = CrawlerProcess(get_project_settings())

    # start two spider
    process.crawl('members')
    process.start()
