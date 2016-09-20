#!/bin/bash

REDIS=$(dpkg -l redis-server)
if  [ "$REDIS" == "" ]; then
    sudo apt-get install redis-server
fi 



sudo apt-get update && sudo apt-get install build-essential autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus python-qt4 python-qt4-gl libgle3 python-dev libxml2-dev libxslt1-dev zlib1g-dev libssl-dev virtualenv


if [ ! -d "engineenv" ]; then
    virtualenv engineenv
fi


source engineenv/bin/activate

pip install -r requirements.txt
