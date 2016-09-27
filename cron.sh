#!/bin/bash
echo "Init Luigi at  $(date)." >> /var/log/luigi/processes.log
cd /home/enreda/tipi-engine
source engineenv/bin/activate
python base.py

echo "Finish luigi at $(date). ">> /var/log/luigi/processes.log
echo "****************">> /var/log/luigi/processes.log
