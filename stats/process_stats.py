import sys
sys.path.append("../")
from database.congreso import Congress
import copy
from operator import itemgetter
import pdb


class InsertStats(object):
    _curdict = None
    _dbmanager = None
    dictforinsert = None
    def __init__(self):
        self._dbmanager = Congress()
        self._curdict=self._dbmanager.searchByparam(collection="dicts", param={'group': 'tipi'})
        self.dictforinsert = dict()
        self.stats()

    def stats(self):
        self.deleteAll()
        self.initiatives()
        self.overall()
        self.bydeputies()
        self.byGroups()
        self.latest()
        self.insertstats()

    def initiatives(self): 
        self.dictforinsert['initiatives'] = {}
        self.dictforinsert['initiatives']['all'] = self._dbmanager.countAllInitiatives()
        self.dictforinsert['initiatives']['tipi'] = self._dbmanager.countTipiInitiatives()


    def overall(self):
        self.dictforinsert['overall'] = []
        pipeline=[{ '$match': {'is.tipi': True} }, { '$unwind': '$dicts.tipi' }, { '$group': { '_id': '$dicts.tipi', 'count': { '$sum': 1 } } } ]
        dataset = self._dbmanager.getAgregatefrompipeline(collection="iniciativas",pipeline=pipeline)
        for element in dataset:
            self.dictforinsert['overall'].append(element)

    def bydeputies(self):
        self.dictforinsert['bydeputies'] = []
        dictscopy=copy.copy(self._curdict)

        for element in dictscopy:
            pipeline = [{'$match': {'dicts.tipi':element['name'],'is.tipi': True}}, {'$unwind': '$autor_diputado'},
                        {'$group': {'_id': '$autor_diputado', 'count': {'$sum': 1}}}]
            dataset = self._dbmanager.getAgregatefrompipeline(collection="iniciativas", pipeline=pipeline)
            if len(dataset)>0:
                subdoc=dict()
                subdoc['_id']= element['name']
                subdoc['deputies']=sorted(dataset, key=itemgetter('count'), reverse=True)[:3]
                self.dictforinsert['bydeputies'].append(subdoc)

    def byGroups(self):
        self.dictforinsert['bygroups'] = []
        dictscopy=copy.copy(self._curdict)

        for element in dictscopy:
            pipeline = [{'$match': {'dicts.tipi':element['name'],'is.tipi': True}}, {'$unwind': '$autor_grupo'},
                        {'$group': {'_id': '$autor_grupo', 'count': {'$sum': 1}}}]
            dataset = self._dbmanager.getAgregatefrompipeline(collection="iniciativas", pipeline=pipeline)
            if len(dataset)>0:
                subdoc=dict()
                subdoc['_id']= element['name']
                subdoc['groups']=sorted(dataset, key=itemgetter('count'), reverse=True)[:3]
                self.dictforinsert['bygroups'].append(subdoc)

    def latest(self):
        self.dictforinsert['latest'] = []
        pipeline=[ { '$match': {'is.tipi': True} }, { '$sort': {'actualizacion': -1} }, { '$unwind': '$dicts.tipi' },
                   { '$group': { '_id': '$dicts.tipi' ,
                                 'items':{'$push':{ 'id': "$_id", 'titulo': "$titulo", 'fecha': "$actualizacion",'lugar': "$lugar",'autor': "$autor_diputado"  }}} } ]
        dataset = self._dbmanager.getAgregatefrompipeline(collection="iniciativas", pipeline=pipeline)
        for element in dataset:
            subdoc=dict()
            subdoc['_id'] = element['_id']
            subdoc['items'] = sorted(element['items'], key=itemgetter('fecha'), reverse=True)[:10]
            self.dictforinsert['latest'].append(subdoc)

    def deleteAll(self):
        self._dbmanager.deletecollection("tipistats")

    def insertstats(self):
        self._dbmanager.insertstat(dict=self.dictforinsert)


if __name__ == "__main__":
    a = InsertStats()
