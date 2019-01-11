# Ths Python file uses the following encoding: utf-8
import sys
from time import time
import itertools
import pcre
import pymongo 

from database.congreso import Congress

reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')


class LabelingEngine:

    def run(self):
        dbmanager = Congress()
        regex_engine = RegexEngine()
        topics = list(dbmanager.getTopics())
        initiatives = dbmanager.getNotTaggedInitiatives()
        i = 1
        total = initiatives.count()
        if topics:
            for initiative in initiatives:
                try:
                    print "Tagging initiative %d of %d:" % (i, total)
                    if initiative.has_key('title') or initiative.has_key('content'):
                        regex_engine.loadInitiative(initiative)
                        for topic in topics:
                            regex_engine.loadTags(topic)
                            regex_engine.matchTags()
                        initiative['topics'] = regex_engine.getTopicsFound()
                        initiative['tags'] = regex_engine.getTagsFound()
                        dbmanager.taggingInitiative(initiative['_id'], regex_engine.getTopicsFound(), regex_engine.getTagsFound())
                        if regex_engine.getTopicsFound():
                            dbmanager.addInitiativeAlert(initiative)
                except Exception, e:
                    print e
                    print "Error tagging the initiative " + str(initiative['_id'])
                regex_engine.cleanTopicsAndTagsFound()
                i += 1
            print '============================'




class RegexEngine:
    
    def __init__(self):
        self.__tags = []
        self.__initiative = []
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
                                })
                else:
                    new_tags.append(tag)
        return new_tags

    def loadTags(self, topic):
        self.__tags = []
        for tag in self.__shuffleTags(topic['tags']):
            self.__tags.append({
                'topic': topic['name'],
                'compiletag': pcre.compile('(?i)'+tag['regex']),
                'tag': tag['original'],
                'subtopic': tag['subtopic'],
                'struct': {'tag': tag['tag'], 'subtopic': tag['subtopic'], 'topic': topic['name']}
                })

    def loadInitiative(self, initiative):
        self.__initiative = initiative
    
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

    def getinitiative(self):
        return self.__initiative

    def addTagsToFounds(self, tag):
        if tag['struct'] not in self.__tags_struct_found:
            self.__tags_struct_found.append(tag['struct'])
            if tag['topic'] not in self.__topics_found:
                self.__topics_found.append(tag['topic'])

    def matchTags(self):
        tags = self.getTags()
        initiative = self.getinitiative()
        if initiative.has_key('title'):
            if not initiative.has_key('content'):
                initiative['content'] = []
            initiative['content'].append(initiative['title'])
        for line in initiative['content']:
            if isinstance(line, list) and len(line) > 0:
                line = line[0]
            for tag in tags:
                try:
                    if pcre.search(tag['compiletag'], line):
                        self.addTagsToFounds(tag)
                except Exception, e:
                    print str(e) + " : " + str(tag['tag']) + " || on initiative " + str(initiative['_id'])
                    break
