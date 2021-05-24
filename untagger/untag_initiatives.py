from copy import deepcopy
import pickle
import codecs

import tipi_tasks
from tipi_data.models.topic import Topic
from tipi_data.models.initiative import Initiative, Tag

from logger import get_logger
from alerts.settings import USE_ALERTS


log = get_logger(__name__)


class UntagInitiatives:

    def untag_all(self):
        print('Untagging all initiatives')
        Initiative.all().update(tagged=False)

    def undo(self):
        print('Marking all initiatives as tagged')
        Initiative.all().update(tagged=True)

    def by_topic(self, topic):
        print('Untagging topic "' + topic + '"')
        Initiative.all(topics=topic).update(tagged=False)

    def by_tag(self, tag):
        print('Untagging tag "' + tag + '"')
        Initiative.all(tags__tag=tag).update(tagged=False)

    def remove_topic(self, topic):
        print('Removing topic "' + topic + '"')
        Initiative.all().update(pull__topics=topic)

    def remove_tag(self, tag):
        print('Removing tag "' + tag + '"')
        Initiative.all().update(pull__tags__tag=tag)
