# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrap.denylist import Denylist
from scrap.items import InitiativeItem,\
                        FinishTextItem,\
                        AmendmentItem,\
                        ResponseItem

from database.congreso import Congress


class MongoDBPipeline(object):

    def process_item(self, item, spider):

        if isinstance(item, InitiativeItem):

            try:
                if Denylist.isFinalState(item['processing']):
                    Denylist.addElement(item['url'])

            except Exception as e:
                print("**** FAILURE: {} *****".format(e))
            congress = Congress()
            search = congress.getInitiative(
                    reference=item['reference'],
                    initiative_type_alt=item['initiative_type_alt'],
                    title=item['title'])

            if congress.isDiffInitiative(item=item, search=search):
                # Update
                congress.updateorinsertInitiativecontent(item=item, type='update')

            elif not search:
                # Does not exist (just insert)
                congress.updateorinsertInitiativecontent(item=item, type='insert')
            else:
                # It is the same initiative
                print("It is the same, nothing change")


        elif isinstance(item, AmendmentItem):
            congress = Congress()
            search = congress.getAdmendment(
                    reference=item['reference'],
                    initiative_type_alt=item['initiative_type_alt'],
                    parliamentarygroup=item['author_parliamentarygroups'])

            # Esta de otra forma estructurado
            congress.updateorinsertAdmenment(item=item, search=search)

        elif isinstance(item, FinishTextItem):
            congress = Congress()
            search = congress.getInitiative(
                    reference=item['reference'],
                    initiative_type_alt=item['initiative_type_alt'],
                    title=item['title'])
            if congress.isDiffInitiative(item=item, search=search):
                # Update
                congress.updateorinsertFinishtextorResponse(item=item, type='update')

            elif not search:
                # Does not exist (just insert)
                congress.updateorinsertFinishtextorResponse(item=item, type='insert')
            else:
                # It is the same initiative
                print("It is the same, nothing change")

        elif isinstance(item, ResponseItem):
            congress = Congress()
            search = congress.getInitiative(
                    reference=item['reference'],
                    initiative_type_alt=item['initiative_type_alt'],
                    title=item['title'])
            if congress.isDiffInitiative(item=item, search=search):
                # Update
                congress.updateorinsertFinishtextorResponse(item=item, type='update')

            elif not search:
                # Does not exist (just insert)
                congress.updateorinsertFinishtextorResponse(item=item, type='insert')
            else:
                # It is the same initiative
                print("It is the same, nothing change")

        return item


    def hasKey(self, item, tag):
        return [key for key in item.keys() if tag is key]
