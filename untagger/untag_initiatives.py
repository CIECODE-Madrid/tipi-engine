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
        Initiative.all().update(unset__tagged=1)

    def by_kb(self, kb):
        print('Untagging knowledge base "' + kb + '"')
        Initiative.all().update(pull_tagged__knowledgebase=kb)

    def by_topic(self, topic):
        print('Untagging topic "' + topic + '"')
        Initiative.all().update(pull_tagged__topics=topic)

    def by_tag(self, tag):
        print('Untagging tag "' + tag + '"')
        Initiative.all().update(pull_tagged__tags__tag=tag)
