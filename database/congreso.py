# -*- coding: utf-8 -*-
import re, random, time, datetime
from conn import MongoDBconn



class Congress(object):
    _conn = None
    def __init__(self):
        self._conn = MongoDBconn()

    def _getCollection(self, collection):
        return self._conn.getDB()[collection]

    def searchAll(self, collection):
        return [ element for element in self._getCollection(collection).find()]

    def searchByParams(self, collection, param={}):
        return self._getCollection(collection).find(param)

    def countTipiInitiatives(self):
        return self._getCollection('initiatives').find({'is.tipi': True}).count()

    def countAllInitiatives(self):
        return self._getCollection('initiatives').find().count()

    def getNotAnnotatedInitiatives(self, topic):
        return self._getCollection('initiatives').find({'$or': [{'annotate.%s'%topic : {'$exists': False}}, {'annotate.%s'%topic : False}]}, no_cursor_timeout=True)

    def getDeputyByName(self, name):
        return list(self._getCollection('deputies').find({'name': name}))[0]

    def getBestDeputyByTopic(self, topic):
        random.seed(time.time())
        bydeputies = list(self._getCollection('tipistats').find({}, {'bydeputies': 1}))
        bydeputy = filter(lambda bydeputy: bydeputy['_id'] == topic, bydeputies[0]['bydeputies'])
        return random.choice(bydeputy[0]['deputies'])['_id']

    def getParliamentaryGroupByName(self, name):
        return list(self._getCollection('parliamentarygroups').find({'name': name}))[0]

    def getBestParliamentaryGroupByTopic(self, topic):
        random.seed(time.time())
        bygroups = list(self._getCollection('tipistats').find({}, {'bygroups': 1}))
        bygroup = filter(lambda bygroup: bygroup['_id'] == topic, bygroups[0]['bygroups'])
        return random.choice(bygroup[0]['groups'])['_id']

    def getTopicsByGroup(self, group):
        return self._getCollection('topics').find({'group': group})

    def getTopicByGroup(self, group):
        return self._getCollection('topics').find({'group': group}, {'name': 1, 'slug': 1})

    def annotateInitiative(self, initiative_id, topicgroup, topics, tags):
        coll = self._getCollection('initiatives')
        coll.update_one({
            '_id': initiative_id,
        },{
            '$set': {
            'annotate.%s'%topicgroup: True,
            'is.%s'%topicgroup: True if len(topics) > 0 else False,
            'topics.%s'%topicgroup: topics,
            'tags.%s'%topicgroup: tags,
            }
        ,}
        )


    def getTopicGroups(self):
        return self._getCollection('topics').find({}, {'group': 1}).distinct('group')
    

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
            print "Not type accepted"
            raise

    def _insertInitiative(self, item):
        item_to_insert = dict(item)
        item_to_insert["updated"] = item_to_insert['created']
        # TODO Create SHA1 _id
        self._getCollection('initiatives').insert(item_to_insert)

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
                    'updated': datetime.datetime.utcnow(),
                    'ended': item['ended']
                }
            })


    def updateorinsertInitiativecontent(self, type="insert", item=None):
        # Pipeline method
        if type is 'insert':
            self._insertInitiative(item)
        elif type is 'update':
            self._updateInitiativecontent(item)
        else:
            print "Not type accepted"
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
            'updated': datetime.datetime.utcnow(),
            'ended': item['ended']
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
                    'topics':1,
                    'tags':1,
                    'is':1,
                    'annotate':1
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
                if key == ikey and (key != 'updated') and (key != 'content' and  key != 'topics' and key != 'tags' and key != 'annotate' and key != 'is'):
                    if value != ivalue:
                        return False
        return True


    def updateorinsertAdmenment(self, item = None ,search = None):
        # Pipeline method
        self._insertAdmendment(item, search)


    def _insertAdmendment(self, item, search):
        if not search:
            # TODO Create SHA1 _id
            insert = {
                'title': item['title'],
                'reference': item['reference'],
                'initiative_type':item['initiative_type'],
                'initiative_type_alt':item['initiative_type_alt'],
                'author_deputies': item['author_deputies'],
                'author_parliamentarygroups': item['author_parliamentarygroups'],
                'author_others': item['author_others'],
                'created': item["created"],
                'updated': item["created"],
                'ended': item["ended"],
                'url': item['url'],
                'place': item['place'],
                'processing': item['processing'],
                'content':[item["content"]]
            }
            self._getCollection('initiatives').insert(insert)
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
                    'content': before,
                    'updated': datetime.datetime.utcnow()
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
            print "Not type accepted"
            raise

    def _insertFinishsTextorResponse(self, item):
        item_to_insert = dict(item)
        item_to_insert["updated"] = item_to_insert['created']
        self._getCollection('initiatives').insert(item_to_insert)

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
                    'updated': datetime.datetime.utcnow(),
                    'ended': item['ended'],
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
            print "Not type accepted"
            raise

    def _insertDeputy(self, item):
        self._getCollection('deputies').insert(dict(item))

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



    def addAlert(self, dictname, init_id, init_title, init_date):
        self._getCollection('tipialerts').update_one({
            'dict': dictname,
            }, {
                '$addToSet': {
                    'items': {
                        'id': str(init_id),
                        'title': init_title,
                        'date': init_date,
                        }
                }
            }, upsert=True)

    def getTipisAllAlerts(self):
        return self._getCollection('tipialerts').find({'items':{'$exists':True,'$not':{'$size':0}}})

    def getUserswithAlert(self):
        return self._getCollection('users').find({"profile.dicts":{'$exists': True}})

    def getAggregatedInitiativesByPipeline(self, pipeline):
        return list(self._getCollection('initiatives').aggregate(pipeline=pipeline))

    def deletecollection(self,collection):
        #Warning
        self._getCollection(collection).drop()

    def insertstat(self, dict={}):
        self._getCollection('tipistats').insert(dict)
