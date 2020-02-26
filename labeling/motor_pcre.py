from time import time
import itertools
import pcre
import pymongo

from database.congreso import Congress
from alerts.settings import USE_ALERTS


class LabelingEngine:

    def run(self):
        dbmanager = Congress()
        dbmanager.deleteCollection('initiatives_alerts')
        regex_engine = RegexEngine()
        topics = list(dbmanager.getTopics())
        initiatives = dbmanager.getNotTaggedInitiatives()
        i = 1
        total = initiatives.count()
        if topics:
            for initiative in initiatives:
                try:
                    print("Tagging initiative %d of %d:" % (i, total))
                    if 'title' in initiative.keys() or 'content' in initiative.keys():
                        regex_engine.loadInitiative(initiative)
                        for topic in topics:
                            regex_engine.loadTags(topic)
                            regex_engine.matchTags()
                        topics_found = regex_engine.getTopicsFound()
                        tags_found = regex_engine.getTagsFound()
                        initiative['topics'] = topics_found
                        initiative['tags'] = tags_found
                        dbmanager.taggingInitiative(initiative['_id'], topics_found, tags_found)
                        if topics_found and USE_ALERTS:
                            dbmanager.addInitiativeAlert(initiative)
                except Exception:
                    print("Error tagging the initiative " + str(initiative['_id']))
                regex_engine.cleanTopicsAndTagsFound()
                i += 1
            print('============================')


class RegexEngine:

    def __init__(self):
        self.__tags = []
        self.__initiative = []
        self.__topics_found = []
        self.__tags_found = []

    def __shuffleTags(self, tags):
        new_tags = []
        for tag in tags:
            if tag is not None:
                tag['original'] = tag['regex']
                if tag['shuffle']:
                    delimiter = '.*?' if '.*?' in tag['regex'] else '.*'
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
                'subtopic': tag['subtopic'],
                'tag': tag['tag'],
                'compiletag': pcre.compile('(?i)'+tag['regex']),
                })

    def loadInitiative(self, initiative):
        self.__initiative = initiative

    def getTags(self):
        return self.__tags

    def cleanTopicsAndTagsFound(self):
        self.__topics_found = []
        self.cleanTagsFound()

    def getTopicsFound(self):
        return sorted(list(set([tag['topic'] for tag in self.__tags_found])))

    def getTagsFound(self):
        return sorted(self.__tags_found, key=lambda t: (t['topic'], t['subtopic'], t['tag']))

    def __appendTagToFounds(self, new_tag):
        found = False
        for tag in self.__tags_found:
            if tag['topic'] == new_tag['topic'] \
                    and tag['subtopic'] == new_tag['subtopic'] \
                    and tag['tag'] == new_tag['tag']:
                        found = True
                        tag['times'] = tag['times'] + new_tag['times']
                        break
        if not found:
            self.__tags_found.append(new_tag)

    def cleanTagsFound(self):
        self.__tags_found = []

    def getinitiative(self):
        return self.__initiative

    def matchTags(self):
        tags = self.getTags()
        initiative = self.getinitiative()
        if 'title' in initiative.keys():
            if not 'content' in initiative.keys():
                initiative['content'] = []
            initiative['content'].append(initiative['title'])
        for line in initiative['content']:
            if isinstance(line, list) and len(line) > 0:
                line = line[0]
            for tag in tags:
                try:
                    result = pcre.findall(tag['compiletag'], line)
                    times = len(result)
                    if times > 0:
                        tag_copy = tag.copy()
                        tag_copy.pop('compiletag')
                        tag_copy['times'] = times
                        self.__appendTagToFounds(tag_copy)
                except Exception:
                    print(str(tag['tag']) + " || on initiative " + str(initiative['_id']))
                    break
