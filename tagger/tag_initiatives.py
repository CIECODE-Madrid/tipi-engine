import time
import itertools
import pickle
import codecs

import pcre

import tipi_tasks
from tipi_data.models.topic import Topic

from database.congreso import Congress
from alerts.settings import USE_ALERTS


class TagInitiatives:

    def run(self):
        dbmanager = Congress()
        dbmanager.deleteCollection('initiatives_alerts')
        tags = codecs.encode(pickle.dumps(Topic.get_tags()), "base64").decode()
        initiatives = dbmanager.getNotTaggedInitiatives()
        total = initiatives.count()
        for index, initiative in enumerate(initiatives):
            try:
                print("\rTagging initiative %d of %d\n" % ((index+1), total), end="")
                initiative['content'].append(initiative['title'])
                text = '.'.join(initiative['content'])
                tipi_tasks.init()
                result = tipi_tasks.tagger.extract_tags_from_text(text, tags)
                if 'result' in result.keys():
                    result = result['result']
                    initiative['topics'] = result['topics']
                    initiative['tags'] = result['tags']
                    dbmanager.taggingInitiative(
                            initiative['_id'],
                            result['topics'],
                            result['tags'])
                    if result['topics'] and USE_ALERTS:
                        dbmanager.addInitiativeAlert(initiative)
            except Exception as e:
                print("Error tagging {}: {}".format(initiative['_id'], e))
