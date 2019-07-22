# -*- coding: utf-8 -*-
import re, random, time, datetime
from .conn import MongoDBconn
from utils import generateId

from scraper.scrap.scrap.scrap.congreso_settings import ID_LEGISLATURA


class Congress(object):
    _conn = None
    def __init__(self):
        self._conn = MongoDBconn()

    def _getCollection(self, collection):
        return self._conn.getDB()[collection]

    def searchAll(self, collection):
        return [element for element in self._getCollection(collection).find()]

    def searchByParams(self, collection, param={}):
        return self._getCollection(collection).find(param)

    def countAllInitiatives(self):
        return self._getCollection('initiatives').find().count()

    def countTaggedInitiatives(self):
        return self._getCollection('initiatives').find({'topics': {'$exists': True, '$not': {'$size': 0}}}).count()

    def getNotTaggedInitiatives(self):
        return self._getCollection('initiatives').find({'$or': [{'tagged': {'$exists': False}}, {'tagged': False}]}, no_cursor_timeout=True)

    def getDeputyByName(self, name):
        return list(self._getCollection('deputies').find({'name': name}))[0]

    def getBestDeputyByTopic(self, topic):
        random.seed(time.time())
        deputiesByTopics = list(self._getCollection('statistics').find({}, {'deputiesByTopics': 1}))
        deputiesByTopic = filter(
                lambda deputiesByTopic: deputiesByTopic['_id'] == topic,
                deputiesByTopics[0]['deputiesByTopics']
                )
        return random.choice(deputiesByTopic[0]['deputies'])['_id']

    def getParliamentaryGroupByName(self, name):
        return list(self._getCollection('parliamentarygroups').find({'name': name}))[0]

    def getBestParliamentaryGroupByTopic(self, topic):
        random.seed(time.time())
        pgByTopics = list(self._getCollection('statistics').find({}, {'parliamentarygroupsByTopics': 1}))
        pgByTopic = filter(
                lambda pgByTopic: pgByTopic['_id'] == topic,
                pgByTopics[0]['parliamentarygroupsByTopics']
                )
        return random.choice(pgByTopic[0]['parliamentarygroups'])['_id']

    def getTopics(self, simplified=False):
        if simplified:
            return self._getCollection('topics').find({}, {'name': 1, 'slug': 1})
        return self._getCollection('topics').find()

    def getSimplifiedTopics(self):
        return self._getCollection('topics').find({'group': group}, {'name': 1, 'slug': 1})

    def taggingInitiative(self, initiative_id, topics, tags):
        coll = self._getCollection('initiatives')
        coll.update_one({
            '_id': initiative_id,
        },{
            '$set': {
                'topics': topics,
                'tags': tags,
                'tagged': True,
            }
        ,}
        )

    def getSubtopics(self):
        return self._getCollection('initiatives').distinct('tags.subtopic')

    def getInitiatives(self):
        return self._getCollection('initiatives').find()

    def getInitiative(self, reference = None, initiative_type_alt= None, title = None):
        return self._getCollection('initiatives').find_one(
            {
                'reference': reference,
                'initiative_type_alt': initiative_type_alt,
                'title': title
            }
        )

    def updateorinsertInitiative(self, type = "insert", item = None):
        # Pipeline method
        if type is 'insert':
            self._insertInitiative(item)
        elif type is 'update':
            self._updateInitiative(item)
        else:
            print("Not type accepted")
            raise

    def _insertInitiative(self, item):
        initiative = dict(item)
        initiative['_id'] = self._generateIdFromInitiative(initiative)
        self._getCollection('initiatives').insert(initiative)

    def _updateInitiative(self, item):
        self._getCollection('initiatives').update_one({
                'reference': item['reference'],
                'initiative_type_alt': item['initiative_type_alt']
            },{
                '$set': {
                    'title': item['title'],
                    'author_deputies': item['author_deputies'],
                    'author_parliamentarygroups': item['author_parliamentarygroups'],
                    'author_others': item['author_others'],
                    'url': item['url'],
                    'initiative_type': item['initiative_type'],
                    'processing': item['processing'],
                    'place': item['place'],
                    'created': item['created'],
                    'updated': item['updated']
                }
            })

    def updateorinsertInitiativecontent(self, type="insert", item=None):
        # Pipeline method
        if type is 'insert':
            self._insertInitiative(item)
        elif type is 'update':
            self._updateInitiativecontent(item)
        else:
            print("Not type accepted")
            raise

    def _updateInitiativecontent(self, item):
        self._getCollection('initiatives').update_one({
                 'reference': item['reference'],
                'initiative_type_alt': item['initiative_type_alt']
        },{
            '$set': {
                'content': item['content'],
                'title': item['title'],
                'author_deputies': item['author_deputies'],
                'author_parliamentarygroups': item['author_parliamentarygroups'],
                'author_others': item['author_others'],
                'url': item['url'],
                'initiative_type': item['initiative_type'],
                'processing': item['processing'],
                'place': item['place'],
                'created': item['created'],
                'updated': item['updated']
            }
        })

    def isDiffInitiative(self, item=None, search=None):
        if not search:
            return False
        return not self.sameInitiative(item, search)

    def deletefields(self, search):
        coll = self._getCollection('initiatives')
        coll.update_one({
                'reference': search['reference'],
                'initiative_type_alt': search['initiative_type_alt']
            },
            {
                '$unset':
                {
                    'topics': 1,
                    'tags': 1,
                    'tagged': 1,
                }
            },False,True)

    def notEnmienda(self, url):
            return self._getCollection('initiatives').find({"$and": [{'url':url},{"initiative_type_alt":{"$not":re.compile('Enmienda')}}]}).count()

    def sameInitiative(self, item, search):
        if not search["content"] and item['content'] and self.notEnmienda(search['url'])>0:
            self.deletefields(search)
            return False
        if search:
            if search['processing'] != item['processing']:
                return False
        return True

    def sameAdmendment(self,item,search):
        for key, value in search.iteritems():
            for ikey,ivalue in item.iteritems():
                if key == ikey and (key != 'updated') and (key != 'content' and  key != 'topics' and key != 'tags' and key != 'tagged'):
                    if value != ivalue:
                        return False
        return True

    def updateorinsertAdmenment(self, item = None ,search = None):
        # Pipeline method
        self._insertAdmendment(item, search)

    def _insertAdmendment(self, item, search):
        if not search:
            initiative = dict(item)
            initiative['_id'] = self._generateIdFromInitiative(initiative)
            initiative['updated'] = initiative["created"]
            self._getCollection('initiatives').insert(initiative)
        else:
            self._updateAdmendment(item, search)

    def _updateAdmendment(self, item, search):
        parliamentarygroups = item["author_parliamentarygroups"]
        coll = self._getCollection('initiatives')
        append = item["content"]
        before = search["content"]
        before_deputies = search["author_deputies"]
        before_others = search["author_others"]
        if item["author_deputies"]:
            before_deputies = before_deputies + item["author_deputies"]
        if item["author_others"]:
            before_others = before_others + item["author_others"]
        if append not in before:
            before.append(append)
            coll.update_one({
                        'reference': item['reference'],
                        'initiative_type_alt': item['initiative_type_alt'],
                        'author_parliamentarygroups': parliamentarygroups
                },{
                    '$set': {
                    'author_deputies': list(set(before_deputies)),
                    'author_others': list(set(before_others)),
                    'content': before
                    }
                })

    def getAdmendment(self, reference=None, initiative_type_alt=None, parliamentarygroup=None):
        return self._getCollection('initiatives').find_one(
        {
                'reference': reference,
                'initiative_type_alt': initiative_type_alt,
                'author_parliamentarygroups': parliamentarygroup
        })

    def updateorinsertFinishtextorResponse(self, type="insert", item=None):
        # Pipeline method
        if type is 'insert':
            self._insertFinishsTextorResponse(item)
        elif type is 'update':
            self._updateFinishTextorResponse(item)
        else:
            print("Not type accepted")
            raise

    def _insertFinishsTextorResponse(self, item):
        initiative = dict(item)
        initiative['_id'] = self._generateIdFromInitiative(initiative)
        initiative["updated"] = initiative['updated']
        self._getCollection('initiatives').insert(initiative)

    def _updateFinishTextorResponse(self, item):
        self._getCollection('initiatives').update_one({
                'reference': item['reference'],
                'initiative_type_alt': item['initiative_type_alt'],

            }, {
                '$set': {
                    'title': item['title'],
                    'author_deputies': item['author_deputies'],
                    'author_parliamentarygroups': item['author_parliamentarygroups'],
                    'author_others': item['author_others'],
                    'url': item['url'],
                    'initiative_type': item['initiative_type'],
                    'processing': item['processing'],
                    'place': item['place'],
                    'created': item['created'],
                    'updated': item['updated'],
                    'content': item['content']
                }
            })

    def getDeputy(self, name=None):
        return self._getCollection('deputies').find_one({'name': name})

    def updateorinsertDeputy(self, type = "insert", item = None):
        # Pipeline method
        if type is 'insert':
            self._insertDeputy(item)
        elif type is 'update':
            self._updateDeputy(item)
        else:
            print("Not type accepted")
            raise

    def _insertDeputy(self, item):
        # Security check: sometimes item fields are blank
        if item['name']:
            item['_id'] = generateId(item['name'])
            self._getCollection('deputies').insert(item)

    def _updateDeputy(self, item):
        self._getCollection('deputies').update_one({
            'name': item['name'],

        }, {
            '$set': {
                'parliamentarygroup': item['parliamentarygroup'],
                'image': item['image'],
                'email': item['email'],
                'web': item['web'],
                'twitter': item['twitter'],
                'start_date': item['start_date'],
                'end_date': item['end_date'],
                'url': item['url']
            }
        })

    def getAggregatedInitiativesByPipeline(self, pipeline):
        return list(self._getCollection('initiatives').aggregate(pipeline=pipeline))

    def deleteCollection(self, collection):
        self._getCollection(collection).drop()

    def insertStats(self, document={}):
        self._getCollection('statistics').insert(document)

    def deleteAllStats(self):
        self.deleteCollection('statistics')

    def addInitiativeAlert(self, initiative):
        self._getCollection('initiatives_alerts').insert(initiative)

    def deleteAllInitiativesAlerts(self):
        self.deleteCollection('initiatives_alerts')

    def searchInitiativesAlerts(self, search):
        return self._getCollection('initiatives_alerts').find(search, no_cursor_timeout=True)

    def updateInitiativesStatus(self, search, status):
        self._getCollection('initiatives').update_many(
                search,
                {
                    '$set': {
                        'status': status,
                    }
                })

    def updateInitiativeURL(self, _id, reference):
        sref = reference.split("/")
        new_url = "http://www.congreso.es/portal/page/portal/Congreso/Congreso/Iniciativas?_piref73_2148295_73_1335437_1335437.next_page=/wc/servidorCGI&CMD=VERLST&BASE=IW{}&FMT=INITXDSS.fmt&DOCS=1-1&DOCORDER=FIFO&OPDEF=ADJ&QUERY=({}%2F{}*.NDOC.)".format(ID_LEGISLATURA, sref[0], sref[1])
        self._getCollection('initiatives').update_one({
            '_id': _id,
            }, {
                '$set': {
                    'url': new_url
                }
            })
    
    def _generateIdFromInitiative(self, initiative):
        return generateId(
                initiative['reference'],
                u''.join(initiative['author_deputies']),
                u''.join(initiative['author_parliamentarygroups']),
                u''.join(initiative['author_others']),
                )
