#!/bin/bash
cd /home/pi/py
kill `cat vibration_recorder.pid` 
nohup ./vibration_recorder.py 1>/dev/null 2>&1 &
echo $! >vibration_recorder.pid
