import tweepy
from credentials import *



class TweetBotManager:

    def __init__(self):
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        self.api = tweepy.API(self.auth)

    def tweet(self, tbm_obj):
        self.api.update_status(tbm_obj.get_message())
