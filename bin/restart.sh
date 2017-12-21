#!/bin/bash

set -x
kill -9 $(ps aux | grep "Image-Quality-Assessment-Model" | grep -v grep | awk '{print $2}')
root=/home/services/iqa
nohup python $root/src/server.py $root/data/Image-Quality-Assessment-Model > $root/logs/nohup.log 2>&1 &
