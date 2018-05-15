import sys
sys.path.append("../")
from database.congreso import Congress
import copy
from operator import itemgetter
import pdb


class GenerateStats(object):

    topics = None
    dbmanager = None
    document = None

    def __init__(self):
        self.dbmanager = Congress()
        self.topics = self.dbmanager.searchall('topics')
        self.document = dict()
        self.stats()

    def stats(self):
        self.deleteAll()
        self.initiatives()
        self.overall()
        self.byDeputies()
        self.byParliamentaryGroups()
        self.latest()
        self.insertstats()

    def initiatives(self): 
        self.document['initiatives'] = {}
        self.document['initiatives']['all'] = self.dbmanager.countAllInitiatives()
        self.document['initiatives']['tagged'] = self.dbmanager.countTaggedInitiatives()


    def overall(self):
        self.document['overall'] = []
        pipeline = [{ '$match': {'topics': {$exists: True, $not: {$size: 0}}} }, { '$unwind': '$topics' }, { '$group': { '_id': '$topics', 'count': { '$sum': 1 } } } ]
        result = self.dbmanager.getAggregatedInitiativesByPipeline(pipeline=pipeline)
        for element in result:
            self.document['overall'].append(element)

    def byDeputies(self):
        self.document['bydeputies'] = []
        topics = copy.copy(self.topics)

        for element in topics:
            pipeline = [{'$match': { 'topics': element['name'] } }, {'$unwind': '$author_deputies'},
                        {'$group': {'_id': '$author_deputies', 'count': {'$sum': 1}}}]
            result = self.dbmanager.getAggregatedInitiativesByPipeline(pipeline=pipeline)
            if len(result) > 0:
                subdoc = dict()
                subdoc['_id'] = element['name']
                subdoc['deputies'] = sorted(result, key=itemgetter('count'), reverse=True)[:3]
                self.document['bydeputies'].append(subdoc)

    def byParliamentaryGroups(self):
        self.document['byparliamentarygroups'] = []
        topics = copy.copy(self.topics)

        for element in topics:
            pipeline = [{'$match': {'topics':element['name']}}, {'$unwind': '$author_parliamentarygroups'},
                        {'$group': {'_id': '$author_parliamentarygroups', 'count': {'$sum': 1}}}]
            return = self.dbmanager.getAggregatedInitiativesByPipeline(pipeline=pipeline)
            if len(return) > 0:
                subdoc = dict()
                subdoc['_id']= element['name']
                subdoc['parliamentarygroups'] = sorted(result, key=itemgetter('count'), reverse=True)[:3]
                self.document['byparliamentarygroups'].append(subdoc)

    def latest(self):
        self.document['latest'] = []
        pipeline=[ { '$match': {'topics': {$exists: True, $not: {$size: 0}}} }, { '$sort': {'updated': -1} }, { '$unwind': '$topics' },
                   { '$group': { '_id': '$topics' ,
                                 'initiatives':{'$push':{ 'id': "$_id", 'title': "$title", 'date': "$updated",'place': "$place",'author': "$author_deputies"  }}} } ]
        result = self.dbmanager.getAggregatedInitiativesByPipeline(pipeline=pipeline)
        for element in result:
            subdoc = dict()
            subdoc['_id'] = element['_id']
            subdoc['initiatives'] = sorted(element['initiatives'], key=itemgetter('date'), reverse=True)[:20]
            self.document['latest'].append(subdoc)

    def deleteAll(self):
        self.dbmanager.deletecollection("reports")

    def insertstats(self):
        self.dbmanager.insertStats(self.document)


if __name__ == "__main__":
    GenerateStats()
