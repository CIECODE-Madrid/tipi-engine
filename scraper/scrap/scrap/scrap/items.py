# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class InitiativeItemBase(Item):
    title = Field()
    reference = Field()
    initiative_type = Field()
    initiative_type_alt = Field()
    content = Field()
    author_deputies = Field()
    author_parliamentarygroups = Field()
    author_others = Field()
    place = Field()
    processing = Field()
    created = Field()
    ended = Field()
    url = Field()

class InitiativeItem(InitiativeItemBase):
    pass

class AmendmentItem(InitiativeItemBase):
    pass

class FinishTextItem(InitiativeItemBase):
    pass

class ResponseItem(InitiativeItemBase):
    pass



class MemberItem(Item):
    name = Field()
    image = Field()
    parliamentarygroup = Field()
    email = Field()
    web = Field()
    twitter= Field()
    start_date = Field()
    end_date = Field()
    active = Field()
    url = Field()
