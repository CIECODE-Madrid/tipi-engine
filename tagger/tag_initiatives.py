from copy import deepcopy
import pickle
import codecs

import tipi_tasks
from tipi_data.models.topic import Topic
from tipi_data.models.initiative import Initiative, Tag
from tipi_data.models.alert import InitiativeAlert, create_alert

from logger import get_logger
from alerts.settings import USE_ALERTS


log = get_logger(__name__)


class TagInitiatives:

    def __same_field(self, tag1, tag2, field):
        return tag1[field] == tag2[field]

    def __same_tag(self, tag1, tag2):
        return self.__same_field(tag1, tag2, 'topic') \
                and self.__same_field(tag1, tag2, 'subtopic') \
                and self.__same_field(tag1, tag2, 'tag')

    def __delete_topics_with_one_tag_ocurrence(self, result):
        topics_counter = dict()
        for tag in result['tags']:
            if tag['topic'] in topics_counter.keys():
                topics_counter[tag['topic']] += tag['times']
            else:
                topics_counter[tag['topic']] = tag['times']
        for key in topics_counter.keys():
            if topics_counter[key] == 1:
                result['tags'] = list(filter(lambda x: x['topic'] != key, result['tags']))
        result['topics'] = sorted(list(set([tag['topic'] for tag in result['tags']])))

    def __merge_results(self, title_result, body_result):
        DEFAULT_RESULT = {
                'topics': list(),
                'tags': list()
                }
        if len(title_result['tags']) == 0:
            if len(body_result['tags']) > 0:
                return body_result
            return DEFAULT_RESULT
        merged_tags = body_result['tags'].copy()
        for title_tag in title_result['tags']:
            added = False
            for body_tag in body_result['tags']:
                if self.__same_tag(title_tag, body_tag):
                    body_tag['times'] += title_tag['times']
                    added = True
                    break
            if not added:
                merged_tags.append(title_tag.copy())
        return {
                'topics': sorted(list(set([tag['topic'] for tag in merged_tags]))),
                'tags': merged_tags
                }

    def __get_untagged_query(self):
        return {
                '$or': [
                    {'tagged': False},
                    {'tagged': {'$exists': False}},
                    ]
                }

    def tag_initiatives(self, initiatives, tags, merge=False, send_alerts=True):
        total = len(initiatives)
        for index, initiative in enumerate(initiatives):
            try:
                log.info(f"Tagging initiative {index+1} of {total}")
                tipi_tasks.init()
                title_result = tipi_tasks.tagger.extract_tags_from_text(initiative['title'], tags)
                if 'result' not in title_result.keys():
                    continue
                title_result = title_result['result']
                if 'content' not in initiative:
                    result = title_result
                else:
                    text = '.'.join(initiative['content'])
                    body_result = tipi_tasks.tagger.extract_tags_from_text(text, tags)
                    if 'result' not in body_result.keys():
                        continue
                    body_result = body_result['result']
                    result = self.__merge_results(title_result, body_result)
                tags = list(map(
                    lambda x: Tag(
                        topic=x['topic'],
                        subtopic=x['subtopic'],
                            tag=x['tag'],
                        times=x['times']
                        ), result['tags']))

                if merge:
                    topics = list(set(initiative['topics'] + result['topics']))
                    tags = self.merge_tags(initiative['tags'], tags)
                else:
                    topics = result['topics']

                initiative['tags'] = tags
                initiative['topics'] = topics
                self.__delete_topics_with_one_tag_ocurrence(initiative)
                initiative['tagged'] = True
                initiative.save()
                if len(result['topics']) > 0 and USE_ALERTS and send_alerts:
                    create_alert(initiative)
            except Exception as e:
                log.error(f"Error tagging {initiative['id']}: {e}")

    def run(self):
        InitiativeAlert.objects().delete()
        tags = codecs.encode(pickle.dumps(Topic.get_tags()), "base64").decode()
        initiatives = list(Initiative.all(__raw__=self.__get_untagged_query()))
        self.tag_initiatives(initiatives, tags)

    def new_tag(self, tag):
        tag = Topic.get_filtered_tags('tag', tag)
        tags = codecs.encode(pickle.dumps(tag), "base64").decode()
        initiatives = list(Initiative.all())
        self.tag_initiatives(initiatives, tags, True, False)

    def new_topic(self, topic):
        tags = codecs.encode(pickle.dumps(Topic.get_filtered_tags_by_topic(topic)), "base64").decode()
        initiatives = list(Initiative.all())
        self.tag_initiatives(initiatives, tags, True, False)

    def rename(self, old_tag, new_tag):
        initiatives = Initiative.all(tags__tag=old_tag)
        for initiative in initiatives:
            for tag in initiative['tags']:
                if tag.tag == old_tag:
                    tag.tag = new_tag
            initiative.save()

    def merge_tags(self, old_tags, new_tags):
        for new_tag in new_tags:
            if any(old_tag.tag == new_tag.tag for old_tag in old_tags):
                continue
            old_tags.append(new_tag)
        return old_tags
