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
        for groupname in dbmanager.getTopicGroups():
            topics = list(dbmanager.getTopicsByGroup(groupname))
            iniciativas = dbmanager.getNotAnnotatedInitiatives(groupname)
            i = 1
            total = iniciativas.count()
            for iniciativa in iniciativas:
                try:
                    print "%s [%d/%d]:" % (groupname, i, total)
                    if iniciativa.has_key('titulo') or iniciativa.has_key('contenido'):
                        regex_engine.loadIniciativa(iniciativa)
                        for topic in topics:
                            regex_engine.loadTags(topic)
                            regex_engine.matchTags()
                        dbmanager.annotateInitiative(iniciativa['_id'], groupname, regex_engine.getTopicsFound(), regex_engine.getTagsFound())
                        if self.DICTGROUP_WITH_ALERTS == groupname:
                            for topic in regex_engine.getTopicsFound():
                                dbmanager.addAlert(topic, iniciativa['_id'], iniciativa['titulo'], iniciativa['actualizacion'])
                    i += 1
                    regex_engine.cleanTopicsAndTagsFound()
                except Exception, e:
                    regex_engine.cleanTopicsAndTagsFound()
                    print "Error procesando la iniciativa " + str(iniciativa['_id'])
                    break
        print '============================'




class RegexEngine:
    
    def __init__(self):
        self.__tags = []
        self.__iniciativa = []
        self.__topics_found = []
        self.__tags_struct_found = []

    def __shuffleTags(self, tags):
        new_tags = []
        delimiter = '.*'
        for tag in tags:
            if tag is not None:
                tag['original'] = tag['regex']
                if tag['shuffle']:
                    perms = itertools.permutations(tag['regex'].split(delimiter))
                    for perm in perms:
                        new_tags.append({
                                'regex': delimiter.join(perm),
                                'tag': tag['tag'],
                                'subtopic': tag['subtopic'],
                                'original': tag['original']
                                });
                else:
                    new_tags.append(tag)
        return new_tags

    def loadTags(self, topic):
        self.__tags = []
        for tag in self.__shuffleTags(topic['tags']):
            self.__tags.append({
                'topic': topic['name'],
                'group': topic['group'],
                'compiletag': pcre.compile('(?i)'+tag['regex']),
                'tag': tag['original'],
                'subtopic': tag['subtopic'],
                'struct': {'regex': tag['original'], 'tag': tag['tag'], 'topic': topic['name'], 'subtopic': tag['subtopic']}
                });

    def loadIniciativa(self, iniciativa):
        self.__iniciativa = iniciativa
    
    def getTags(self):
        return self.__tags

    def cleanTopicsAndTagsFound(self):
        self.__topics_found = []
        self.cleanTagsFound()

    def getTopicsFound(self):
        return self.__topics_found

    def getTagsFound(self):
        return self.__tags_struct_found

    def cleanTagsFound(self):
        self.__tags_struct_found = []

    def getIniciativa(self):
        return self.__iniciativa

    def addTagsToFounds(self, tag):
        if tag['struct'] not in self.__tags_struct_found:
            self.__tags_struct_found.append(tag['struct'])
            if tag['topic'] not in self.__topics_found:
                self.__topics_found.append(tag['topic'])

    def matchTags(self):
        tags = self.getTags()
        iniciativa = self.getIniciativa()
        if iniciativa.has_key('titulo'):
            if not iniciativa.has_key('contenido'):
                iniciativa['contenido'] = []
            iniciativa['contenido'].append(iniciativa['titulo'])
        for line in iniciativa['contenido']:
            if isinstance(line, list) and len(line) > 0:
                line = line[0]
            for tag in tags:
                try:
                    if pcre.search(tag['compiletag'], line):
                        self.addTagsToFounds(tag);
                except Exception, e:
                    print str(e) + " : " + str(term['term']) + " || en iniciativa " + str(iniciativa['_id'])
                    break


if __name__ == '__main__':
    labeling_engine = LabelingEngine()
    labeling_engine.run()
