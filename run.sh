#/bin/bash

cd /app
python base.py >> /var/log/cron.log 2>&1
