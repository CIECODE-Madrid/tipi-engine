import sys
sys.path.append("../")
from database.congreso import Congress
from operator import itemgetter


class GenerateStats(object):

    topics = None
    dbmanager = None
    document = None

    def __init__(self):
        self.dbmanager = Congress()
        self.topics = self.dbmanager.searchAll('topics')
        self.subtopics = self.dbmanager.getSubtopics()
        self.document = dict()
        self.stats()

    def stats(self):
        self.deleteAll()
        self.overall()
        self.deputiesByTopics()
        self.deputiesBySubtopics()
        self.parliamentarygroupsByTopics()
        self.parliamentarygroupsBySubtopics()
        self.latest()
        self.insertStats()

    def overall(self):
        self.document['overall'] = {
                'initiatives': self.dbmanager.countTaggedInitiatives(),
                'allinitiatives': self.dbmanager.countAllInitiatives(),
                'topics': [],
                'subtopics': []
                }
        pipeline = [{ '$match': {'topics': {'$exists': True, '$not': {'$size': 0}}} }, { '$unwind': '$topics' }, { '$group': { '_id': '$topics', 'initiatives': { '$sum': 1 } } }, {'$sort': {'initiatives': -1}} ]
        result = self.dbmanager.getAggregatedInitiativesByPipeline(pipeline=pipeline)
        for element in result:
            self.document['overall']['topics'].append(element)
        for subtopic in self.subtopics:
            pipeline = [{'$match': { 'tags.subtopic': subtopic } }, { '$group': { '_id': subtopic, 'initiatives': { '$sum': 1 } } } ]
            result = self.dbmanager.getAggregatedInitiativesByPipeline(pipeline=pipeline)
            if len(result) > 0:
                self.document['overall']['subtopics'].append(result[0])
        self.document['overall']['subtopics'].sort(key=lambda x: x['initiatives'], reverse=True)

    def deputiesByTopics(self):
        self.document['deputiesByTopics'] = []
        for element in self.topics:
            pipeline = [{'$match': { 'topics': element['name'] } }, {'$unwind': '$author_deputies'},
                    {'$group': {'_id': '$author_deputies', 'initiatives': {'$sum': 1}}}, {'$sort': {'initiatives': -1}},
                    {'$limit': 10}]
            result = self.dbmanager.getAggregatedInitiativesByPipeline(pipeline=pipeline)
            if len(result) > 0:
                subdoc = dict()
                subdoc['_id'] = element['name']
                subdoc['deputies'] = result
                self.document['deputiesByTopics'].append(subdoc)

    def parliamentarygroupsByTopics(self):
        self.document['parliamentarygroupsByTopics'] = []
        for element in self.topics:
            pipeline = [{'$match': {'topics':element['name']}}, {'$unwind': '$author_parliamentarygroups'},
                    {'$group': {'_id': '$author_parliamentarygroups', 'initiatives': {'$sum': 1}}}, {'$sort': {'initiatives': -1}}]
            result = self.dbmanager.getAggregatedInitiativesByPipeline(pipeline=pipeline)
            if len(result) > 0:
                subdoc = dict()
                subdoc['_id']= element['name']
                subdoc['parliamentarygroups'] = result
                self.document['parliamentarygroupsByTopics'].append(subdoc)

    def deputiesBySubtopics(self):
        self.document['deputiesBySubtopics'] = []
        for element in self.subtopics:
            pipeline = [{'$match': { 'tags.subtopic': element } }, {'$unwind': '$author_deputies'},
                    {'$group': {'_id': '$author_deputies', 'initiatives': {'$sum': 1}}}, {'$sort': {'initiatives': -1}},
                    {'$limit': 10}]
            result = self.dbmanager.getAggregatedInitiativesByPipeline(pipeline=pipeline)
            if len(result) > 0:
                subdoc = dict()
                subdoc['_id'] = element
                subdoc['deputies'] = result
                self.document['deputiesBySubtopics'].append(subdoc)

    def parliamentarygroupsBySubtopics(self):
        self.document['parliamentarygroupsBySubtopics'] = []
        for element in self.subtopics:
            pipeline = [{'$match': { 'tags.subtopic': element } }, {'$unwind': '$author_parliamentarygroups'},
                    {'$group': {'_id': '$author_parliamentarygroups', 'initiatives': {'$sum': 1}}}, {'$sort': {'initiatives': -1}}]
            result = self.dbmanager.getAggregatedInitiativesByPipeline(pipeline=pipeline)
            if len(result) > 0:
                subdoc = dict()
                subdoc['_id']= element
                subdoc['parliamentarygroups'] = result
                self.document['parliamentarygroupsBySubtopics'].append(subdoc)

    def latest(self):
        self.document['latest'] = []
        pipeline = [ { '$match': {'topics': {'$exists': True, '$not': {'$size': 0}}} }, { '$sort': {'updated': -1} }, { '$unwind': '$topics' },
                   { '$group': { '_id': '$topics' ,
                                 'initiatives':{'$push':{ 'id': "$_id", 'title': "$title", 'date': "$updated",'place': "$place",'author': "$author_deputies"  }}} } ]
        result = self.dbmanager.getAggregatedInitiativesByPipeline(pipeline=pipeline)
        for element in result:
            subdoc = dict()
            subdoc['_id'] = element['_id']
            subdoc['initiatives'] = sorted(element['initiatives'], key=itemgetter('date'), reverse=True)[:20]
            self.document['latest'].append(subdoc)

    def deleteAll(self):
        self.dbmanager.deletecollection("statistics")

    def insertStats(self):
        self.dbmanager.insertStats(self.document)


if __name__ == "__main__":
    GenerateStats()
