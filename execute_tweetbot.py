# -*- coding: utf-8 -*-
import sys

from tweetbot.tweetbot import TweetBotManager
from tweetbot.tbmessage import   StaticMessage, \
                        LatestInitiativesByGroupMessage, \
                        LatestInitiativesByBestDeputyMessage, \
                        LatestInitiativesByTopicMessage

# Fist argument indicates the tweet message type

if __name__ == '__main__':
    TBMESSAGES = {
            'static': StaticMessage,
            'topic': LatestInitiativesByTopicMessage,
            'deputy': LatestInitiativesByBestDeputyMessage,
            'group': LatestInitiativesByGroupMessage
            }
    tbm = TweetBotManager()
    tbm.tweet(TBMESSAGES[sys.argv[1]]())
