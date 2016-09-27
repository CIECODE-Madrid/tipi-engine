#!/bin/bash
echo "Init Luigi at  $(date)." >> /var/log/luigi
cd /home/enreda/tipi-engine
source engineenv/bin/activate
python base.py

echo "Finish luigi at $(date). ">> /var/log/luigi
echo "****************">> /var/log/luigi
