#!/bin/bash
# USAGE: bash cron-execute-py-file projectpath filename fileinfo

echo "****************"
echo "Start $3 at $(date)"

cd $1
source engineenv/bin/activate
echo $2

echo "Finish $3 at $(date)"
echo "****************"
