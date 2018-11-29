# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log
import json

from scrap.blacklist import Blacklist
from scrap.items import InitiativeItem, FinishTextItem, AmendmentItem,ResponseItem
from scrap.utils import Utils
from database.congreso import Congress



class MongoDBPipeline(object):

    def process_item(self, item, spider):

        if isinstance(item, InitiativeItem):

            try:
                if Blacklist.isAddedtolist(item['tramitacion']):
                        Blacklist.addElement(item['url'])

            except:
                print ("**** FAILURE *****")
            congress = Congress()
            search = congress.getInitiative(reference=item['reference'], initiative_type_alt=item['initiative_type_alt'], title=item['title'])

            if congress.isDiffInitiative(item=item, search=search):
                    #actualizar
                congress.updateorinsertInitiativecontent(item=item, type='update')

            elif not search:
                    #no existe
                    #insertar sin mas
                congress.updateorinsertInitiativecontent(item=item, type='insert')
            else:
                        #not DIFF
                print "es el mismo, no cambia"



        elif isinstance(item, AmendmentItem):
            congress = Congress()
            search = congress.getAdmendment(reference=item['reference'], initiative_type_alt=item['initiative_type_alt'], parliamentarygroup=item['author_parliamentarygroups'])

            #esta de otra forma estructurado
            congress.updateorinsertAdmenment(item=item, search=search)
        elif isinstance(item, FinishTextItem):
            congress = Congress()
            search = congress.getInitiative(reference=item['reference'], initiative_type_alt=item['initiative_type_alt'], title=item['title'])
            if congress.isDiffInitiative(item=item, search=search):
                #actualizar
                congress.updateorinsertFinishtextorResponse(item=item, type='update')

            elif not search:
                #no existe
                #insertar sin mas
                congress.updateorinsertFinishtextorResponse(item=item, type='insert')
            else:
                    #not DIFF
                print "es el mismo, no cambia"

        elif isinstance(item, ResponseItem):
            congress = Congress()
            search = congress.getInitiative(reference=item['reference'], initiative_type_alt=item['initiative_type_alt'], title=item['title'])
            if congress.isDiffInitiative(item=item, search=search):
                #actualizar
                congress.updateorinsertFinishtextorResponse(item=item, type='update')

            elif not search:
                #no existe
                #insertar sin mas
                congress.updateorinsertFinishtextorResponse(item=item, type='insert')
            else:
                    #not DIFF
                print "es el mismo, no cambia"

        return item


    def hasKey(self, item, tag):
        return [key for key in item.keys() if tag is key]
