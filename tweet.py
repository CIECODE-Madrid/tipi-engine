#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Original script (kept up to date): https://github.com/robincamille/bot-tutorial/blob/master/mybot.py

# Twitter Bot Starter Kit: Bot 1

# This bot tweets three times, waiting 15 seconds between tweets.

# If you haven't changed credentials.py yet with your own Twitter
# account settings

import tweepy, time
from credentials import *
from conn import MongoDBconn
from pymongo import *
from random import randint

# client = MongoClient()
# client = MongoClient("localhost:27017")
# db = client.test
# coll = db.diputados


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)


# What the bot will tweet

tweetlist = ['tweet one!', 'tweet two!']

for line in tweetlist: 
	# rand = randint(0, coll.count())
	# print "Conoces a " + coll.find().limit(-1).skip(rand).next()['nombre']

    api.update_status(line)
    print line
    print '...'
    time.sleep(15) # Sleep for 15 seconds
# conn = MongoDBconn()
print "All done!"