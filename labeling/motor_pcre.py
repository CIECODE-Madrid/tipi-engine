# This Python file uses the following encoding: utf-8
import pcre
import sys
import pymongo 
from time import time
import itertools

from database.congreso import Congress


reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')



class LabelingEngine:
    DICTGROUP_WITH_ALERTS = 'tipi'

    def run(self):
        dbmanager = Congress()
        regex_engine = RegexEngine()
        for groupname in dbmanager.getDictGroups():
            dicts = list(dbmanager.getDictsByGroup(groupname))
            iniciativas = dbmanager.getNotAnnotatedInitiatives(groupname)
            i = 1
            total = iniciativas.count()
            for iniciativa in iniciativas:
                try:
                    print "%s [%d/%d]:" % (groupname, i, total)
                    if iniciativa.has_key('titulo') or iniciativa.has_key('contenido'):
                        regex_engine.loadIniciativa(iniciativa)
                        for dictio in dicts:
                            regex_engine.loadTerms(dictio)
                            regex_engine.matchTerms()
                        dbmanager.addDictsAndTermsToInitiative(iniciativa['_id'], groupname, regex_engine.getDictsFound(), regex_engine.getTermsFound())
                        if self.DICTGROUP_WITH_ALERTS == groupname:
                            for df in regex_engine.getDictsFound():
                                dbmanager.addAlert(df, iniciativa['_id'], iniciativa['titulo'], iniciativa['actualizacion'])
                    i += 1
                    regex_engine.cleanDictsAndTermsFound()
                except Exception, e:
                    regex_engine.cleanDictsAndTermsFound()
                    print "Error procesando la iniciativa " + str(iniciativa['_id'])
                    break
        print '============================'




class RegexEngine:
    
    def __init__(self):
        self.__terms = []
        self.__iniciativa = []
        self.__dicts_found = []
        self.__terms_found = []
        self.__terms_struct_found = []

    def __shuffleTerms(self, terms):
        new_terms = []
        delimiter = '.*'
        for term in terms:
            if term is not None:
                term['original'] = term['term']
                if term['shuffle']:
                    perms = itertools.permutations(term['term'].split(delimiter))
                    for perm in perms:
                        new_terms.append({
                                'term': delimiter.join(perm),
                                'humanterm': term['humanterm'],
                                'original': term['original']
                                });
                else:
                    new_terms.append(term)
        return new_terms

    def loadTerms(self, dict):
        self.__terms = []
        for term in self.__shuffleTerms(dict['terms']):
            self.__terms.append({
                'dict': dict['name'],
                'group': dict['group'],
                'compileterm': pcre.compile('(?i)'+term['term']),
                'term': term['original'],
                'struct': {'term': term['original'], 'humanterm': term['humanterm'], 'dict': dict['name']}
                });

    def loadIniciativa(self, iniciativa):
        self.__iniciativa = iniciativa
    
    def getTerms(self):
        return self.__terms

    def cleanDictsAndTermsFound(self):
        self.__dicts_found = []
        self.cleanTermsFound()

    def getDictsFound(self):
        return self.__dicts_found

    def getTermsFound(self):
        return self.__terms_struct_found

    def cleanTermsFound(self):
        self.__terms_found = []
        self.__terms_struct_found = []

    def getIniciativa(self):
        return self.__iniciativa

    def addTermToFounds(self, term):
        if term['term'] not in self.__terms_found:
            self.__terms_found.append(term['term'])
            self.__terms_struct_found.append(term['struct'])
            if term['dict'] not in self.__dicts_found:
                self.__dicts_found.append(term['dict'])

    def matchTerms(self):
        terms = self.getTerms()
        iniciativa = self.getIniciativa()
        if iniciativa.has_key('titulo'):
            if not iniciativa.has_key('contenido'):
                iniciativa['contenido'] = []
            iniciativa['contenido'].append(iniciativa['titulo'])
        for line in iniciativa['contenido']:
            if isinstance(line, list) and len(line) > 0:
                line = line[0]
            for term in terms:
                try:
                    if pcre.search(term['compileterm'], line):
                        self.addTermToFounds(term);
                except Exception, e:
                    print str(e) + " : " + str(term['term']) + " || en iniciativa " + str(iniciativa['_id'])
                    break


if __name__ == '__main__':
    labeling_engine = LabelingEngine()
    labeling_engine.run()
