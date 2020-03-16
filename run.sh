#!/bin/bash

cd /app
/usr/local/bin/python base.py >> /var/log/cron.log 2>&1
