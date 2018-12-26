# -*- coding: utf-8 -*-

import time
import random
from database.congreso import Congress
from twitteraccount_by_group import TWITTERACCOUNT_BY_GROUP



class TBMessage:

    def __init__(self):
        random.seed(time.time())
        self.dbmanager = Congress()
    
    def random_topic(self):
        random.seed(time.time())
        return random.choice(list(self.dbmanager.getTopics(simplified=True)))

    def get_message(self):
        raise NotImplementedError("Subclass must implement abstract method")


# Every friday
class StaticMessage(TBMessage):

    MESSAGES = [
            u'Busca con nuestro escáner las últimas novedades en el @Congreso_es de los asuntos que más te interesan aquí: https://tipiciudadano.es'
            ]
    
    def get_message(self):
        return random.choice(self.MESSAGES)


class LatestInitiativesByTopicMessage(TBMessage):

    def get_message(self):
        try:
            topic = self.random_topic()
            return u"Descubre aquí cuáles son las últimas iniciativas de %s presentadas en el @Congreso_es, y sus diputadas/os y grupos más activos https://tipiciudadano.es/topics/%s" % (topic['name'].upper(), topic['_id'])
        except:
            pass


class LatestInitiativesByBestDeputyMessage(TBMessage):

    def get_message(self):
        try:
            random_topic_name = self.random_topic()['name']
            best_deputy_name = self.dbmanager.getBestDeputyByTopic(random_topic_name)
            best_deputy = self.dbmanager.getDeputyByName(best_deputy_name)
            if best_deputy['twitter'] == "":
                best_deputy['twitter'] = " ".join(best_deputy_name.split(',').reverse())
            else:
                best_deputy['twitter'] = "@" + best_deputy['twitter'].split('/')[3]
            return u"Éstas son las últimas iniciativas de %s que ha presentado %s, una de las personas con más actividad en el @Congreso_es sobre esta temática: https://tipiciudadano.es/results/topics=%s&deputy=%s" % (random_topic_name.upper(), best_deputy['twitter'], _str_to_url(random_topic_name), _str_to_url(best_deputy_name))
        except:
            pass


class LatestInitiativesByGroupMessage(TBMessage):

    def get_message(self):
        try:
            random_topic_name = self.random_topic()['name']
            best_group_name = self.dbmanager.getBestParliamentaryGroupByTopic(random_topic_name)
            try:
                best_group_twitter = TWITTERACCOUNT_BY_GROUP[best_group_name]
            except:
                best_group_twitter = best_group_name
            return u"Éstas son las últimas iniciativas de %s que ha presentado %s, uno de los grupos parlamentarios más activos en esta temática: https://tipiciudadano.es/results/topics=%s&author=%s" % (random_topic_name.upper(), best_group_twitter, _str_to_url(random_topic_name), _str_to_url(best_group_name))
        except:
            pass




### HELPERS ###

from urllib import quote

def _str_to_url(s):
    return quote(s.encode('utf-8'))
