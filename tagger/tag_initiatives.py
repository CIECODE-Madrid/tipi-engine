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

    def run(self):
        InitiativeAlert.objects().delete()
        tags = codecs.encode(pickle.dumps(Topic.get_tags()), "base64").decode()
        initiatives = Initiative.all.filter(tagged=False)
        total = initiatives.count()
        for index, initiative in enumerate(initiatives):
            try:
                log.info(f"Tagging initiative {index+1} of {total}")
                content = [initiative['title']]
                if 'content' in initiative:
                    content += initiative['content']
                text = '.'.join(content)
                tipi_tasks.init()
                result = tipi_tasks.tagger.extract_tags_from_text(text, tags)
                if 'result' in result.keys():
                    result = result['result']
                    initiative['topics'] = result['topics']
                    initiative['tags'] = list(map(
                        lambda x: Tag(
                            topic=x['topic'],
                            subtopic=x['subtopic'],
                            tag=x['tag'],
                            times=x['times']
                            )
                        ,result['tags']))
                    initiative['tagged'] = True
                    initiative.save()
                    if len(result['topics']) > 0 and USE_ALERTS:
                        create_alert(initiative)
            except Exception as e:
                log.error(f"Error tagging {initiative['id']}: {e}")
