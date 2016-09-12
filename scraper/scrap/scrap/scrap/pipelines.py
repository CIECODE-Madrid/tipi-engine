# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log
import pdb
import json

from scrap.blacklist import Blacklist

from scrap.items import InitiativeItem, FinishTextItem, AmendmentItem,ResponseItem

from scrap.congreso.congreso import Congress

from scrap.utils import Utils


class MongoDBPipeline(object):

    def process_item(self, item, spider):

        if isinstance(item, InitiativeItem):

            try:
                if Blacklist.isAddedtolist(item['tramitacion']):
                        Blacklist.addUrl(item['url'])

            except:
                print ("**** FAILURE *****")
            if not Utils.checkTypewithAmendments(item['tipotexto']):
                congress = Congress()
                search = congress.getInitiative(collection="iniciativas",ref=item['ref'],tipotexto=item['tipotexto'],
                                                titulo=item['titulo'])
                if congress.isDiffinitiative(collection="iniciativas",item=item, search=search):
                    #actualizar
                    congress.updateorinsertInitiative(collection="iniciativas",item=item,type='update')

                elif not search:
                    #no existe
                    #insertar sin mas
                    congress.updateorinsertInitiative(collection="iniciativas",item=item,type='insert')
                else:
                        #not DIFF
                    print "es el mismo, no cambia"
            else:
                congress = Congress()
                search = congress.getInitiative(collection="iniciativas",ref=item['ref'],tipotexto=item['tipotexto'],
                                                titulo=item['titulo'])
                if congress.isDiffinitiative(item=item, search=search):
                    #actualizar
                    congress.updateorinsertInitiativecontent(collection="iniciativas",item=item,type='update')
                elif not search:
                    #no existe
                    #insertar sin mas
                    congress.updateorinsertInitiativecontent(collection="iniciativas",item=item,type='insert')
                else:
                    print "es el mismo, no cambia"


        elif isinstance(item, AmendmentItem):
            congress = Congress()
            search = congress.getAdmendment(collection="iniciativas",ref=item['ref'],tipotexto=item['tipotexto'],
                                            autor=item['autor_grupo'])

            #esta de otra forma estructurado
            congress.updateorinsertAdmenment(collection="iniciativas",item=item,search=search)
        elif isinstance(item, FinishTextItem):
            congress = Congress()
            search = congress.getInitiative(collection="iniciativas",ref=item['ref'],tipotexto=item['tipotexto'],
                                            titulo=item['titulo'])
            if congress.isDiffinitiative(item=item, search=search):
                #actualizar
                congress.updateorinsertFinishtextorResponse(collection="iniciativas",item=item,type='update')

            elif not search:
                #no existe
                #insertar sin mas
                congress.updateorinsertFinishtextorResponse(collection="iniciativas",item=item,type='insert')
            else:
                    #not DIFF
                print "es el mismo, no cambia"

        elif isinstance(item, ResponseItem):
            congress = Congress()
            search = congress.getInitiative(ref=item['ref'],tipotexto=item['tipotexto'],
                                            titulo=item['titulo'])
            if congress.isDiffinitiative(item=item, search=search):
                #actualizar
                congress.updateorinsertFinishtextorResponse(collection="iniciativas",item=item,type='update')

            elif not search:
                #no existe
                #insertar sin mas
                congress.updateorinsertFinishtextorResponse(collection="iniciativas",item=item,type='insert')
            else:
                    #not DIFF
                print "es el mismo, no cambia"

        return item
        #pdb.set_trace()


    def hasKey(self, item, tag):
        return [key for key in item.keys() if tag is key]
