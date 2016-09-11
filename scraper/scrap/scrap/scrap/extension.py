import logging
from scrapy import signals
from scrapy.exceptions import NotConfigured
import pdb

from scrap.items import InitiativeItem,AmendmentItem,FinishTextItem,ResponseItem,MemberItem

logger = logging.getLogger(__name__)

class SpecificItem(object):

    def __init__(self, crawler):
        self.crawler = crawler
        self.initiatives = 0
        self.amendments = 0
        self.finishtext = 0
        self.responses = 0
        self.members = 0
                # connect the extension object to signals
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)


    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


    def spider_closed(self, spider):
        self.crawler.stats.set_value('item/initiatives', self.initiatives)
        self.crawler.stats.set_value('item/amendments', self.amendments)
        self.crawler.stats.set_value('item/finishtext', self.finishtext)
        self.crawler.stats.set_value('item/responses', self.responses)
        self.crawler.stats.set_value('item/members', self.responses)


    def item_scraped(self, item, spider):
        if isinstance(item, InitiativeItem):
            self.initiatives += 1

        elif isinstance(item, AmendmentItem):
            self.amendments += 1

        elif isinstance(item, FinishTextItem):
            self.finishtext += 1
        elif isinstance(item, ResponseItem):
            self.responses += 1
        elif isinstance(item, MemberItem):
            self.responses += 1

