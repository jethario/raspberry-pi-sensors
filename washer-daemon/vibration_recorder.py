#!/usr/bin/env python3

import boto3
import json
import logging
import os
import random
import sys
import time
import uuid
from datetime import datetime
from threading import Timer
from logging.handlers import RotatingFileHandler
from datetime import datetime
from gpiozero import MotionSensor, LED, SmoothedInputDevice
from signal import pause


# sample interval
interval_seconds = 30


# queue
queueUrl = "https://sqs.us-west-2.amazonaws.com/933149874028/WygantSensors"

# flag for motion detection
motion_detected = False

sensor = MotionSensor(pin=4, sample_rate=250, threshold=0.1)


def motion():
    global motion_detected
    # print("motion")
    motion_detected = True


def send_to_queue(message):
    try:
        sqs = boto3.resource('sqs', region_name="us-west-2")
        queue = sqs.Queue(queueUrl)
        response = queue.send_message(
            MessageBody=message
        )
    except Exception as e:
        print(e)


def record():
    global motion_detected
    # time now in seconds
    now_seconds = int(datetime.now().timestamp())

    # json temperature document
    document = {
        "name": "washer",
        "category": "vibration",
        "motion_detected": motion_detected,
        "timestamp": str(now_seconds)
    }

    json_document = json.dumps(document, sort_keys=True)
    # print(json_document)
    send_to_queue(json_document)
    motion_detected = False


def periodic_loop():
    # collect one sample
    try:
        record()
    except Exception as e:
        print(e)


# global
# log = create_logger()


if __name__ == "__main__":
    sensor.when_motion = motion
    while True:
        periodic_loop()
        sys.stdout.flush()
        time.sleep(interval_seconds)
