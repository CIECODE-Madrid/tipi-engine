# This Python file uses the following encoding: utf-8
import pcre
import sys
import pymongo 
from time import time
import itertools


reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')

class MotorRegex:
    
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
        self.cleanTerms()
        print 'Cargando terminos de %s' % dict['name']
        for term in self.__shuffleTerms(dict['terms']):
            print term['term']
            self.__terms.append({
                'dict': dict['name'],
                'group': dict['group'],
                'compileterm': pcre.compile(term['term']),
                'term': term['original'],
                'struct': {'term': term['original'], 'humanterm': term['humanterm']}
                });

    def loadIniciativa(self, iniciativa):
        self.__iniciativa = iniciativa
    
    def getTerms(self):
        return self.__terms

    def cleanTerms(self):
        self.__terms = []
        self.cleanTermsFound()

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

    def matchTerms(self, i):
        print 'Comprobando terminos...'
        self.cleanTermsFound()
        terms = self.getTerms()
        iniciativa = self.getIniciativa()
        if iniciativa.has_key('titulo'):
            if not iniciativa.has_key('contenido'):
                iniciativa['contenido'] = []
            else:
                iniciativa['contenido'] = list(iniciativa['contenido'])
            iniciativa['contenido'].append(iniciativa['titulo'])
        for line in iniciativa['contenido']:
            for term in terms:
                try:
                    if pcre.search(term['compileterm'], line, 0):
                        self.addTermToFounds(term);
                except Exception, e:
                    print str(e) + " : " + str(term['term'])
                    break


if __name__ == '__main__':
    client = pymongo.MongoClient('mongodb://127.0.0.1:3001/')
    db = client['meteor']
    iniciativas = db.iniciativas.find(no_cursor_timeout=True).limit(1)
    # Meter el bucle que trabaje por grupos de diccionarios
    dicts = list(db.dicts.find({'group': 'tipi'}))
    tiempo_inicial = time() 
    m = MotorRegex()
    i = 0
    for iniciativa in iniciativas:
        i += 1
        print "%s [%d]:" % (str(iniciativa['_id']), i)
        try:
            if iniciativa.has_key('titulo') or iniciativa.has_key('contenido'):
                # print 'Cargando la iniciativa'
                m.loadIniciativa(iniciativa)
                for dict in dicts:
                    m.loadTerms(dict)
                    # m.matchTerms(i)
                    # print "[%d en %s]: " % (len(m.getTermsFound()),dict['name'])
        except Exception, e:
            print str(iniciativa['_id']) + ": " + str(e)
            break
        print '============================'
    tiempo_final = time()  
    tiempo_ejecucion = tiempo_final - tiempo_inicial
    # print "El tiempo de ejecucion ha sido ", tiempo_ejecucion
