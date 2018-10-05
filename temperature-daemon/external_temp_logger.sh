#!/bin/bash
cd /home/pi/code
kill `cat external_temp_logger.pid` 
nohup /home/pi/virtualenv/gpio/bin/python3 /home/pi/code/external_temp_logger.py 1>/dev/null 2>&1 &
echo $! >external_temp_logger.pid
