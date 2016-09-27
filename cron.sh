#!/bin/bash
sudo echo "Init Luigi at  $(date)." >> /var/log/luigi/processes.log
cd /home/enreda/tipi-engine
source engineenv/bin/activate
python base.py

sudo echo "Finish luigi at $(date). ">> /var/log/luigi/processes.log
sudo echo "****************">> /var/log/luigi/processes.log
