from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


process = CrawlerProcess(get_project_settings())

# start two spider
process.crawl('initiatives')
process.start()
