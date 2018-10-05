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

import boto3

from temperusb import TemperHandler as TempSensor


# logging settings
log_backups = 3
log_filename = '/var/log/garage_temperature.log'
log_max = 100000

# sample interval
interval_seconds = 30

# queue
queueUrl = "https://sqs.us-west-2.amazonaws.com/933149874028/WygantSensors"


def get_sensor_reading():
    sensor = TempSensor()
    devices = sensor.get_devices()
    sensors = range(devices[0].get_sensor_count())
    # making an assumption here for one device
    temperatures = devices[0].get_temperatures(sensors=sensors)
    # print(temperatures)
    """
    {0: {'ports': 2, 'temperature_f': 83.525, 'sensor': 0, 'temperature_mc': 28625.0, 'temperature_c': 28.625, 'temperature_k': 301.775, 'bus': 1}, 1: {'ports': 2, 'temperature_f': -165.79609375, 'sensor': 1, 'temperature_mc': -109886.71875, 'temperature_c': -109.88671875, 'temperature_k': 163.26328124999998, 'bus': 1}}
    """
    return {
        'fahrenheit': round(temperatures[0]['temperature_f']),
        'celsius': round(temperatures[0]['temperature_c'])
    }


def create_logger():
    log = logging.getLogger('garage')
    log.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(
        log_filename, maxBytes=log_max, backupCount=log_backups)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


def send_to_queue(message):
    try:
        sqs = boto3.resource('sqs')
        queue = sqs.Queue(queueUrl)
        response = queue.send_message(
            MessageBody=message
        )
    except Exception as e:
        print(e)


def record():
    # time now in seconds
    now_seconds = int(datetime.now().timestamp())

    reading = get_sensor_reading()
    # print(reading)
    celsius = reading["celsius"]
    fahrenheit = reading["fahrenheit"]

    # json temperature document
    document = {
        "name": "garage",
        "category": "temperature",
        "celsius": str(celsius),
        "fahrenheit": str(fahrenheit),
        "timestamp": str(now_seconds)
    }

    json_document = json.dumps(document, sort_keys=True)
    log.info(json_document)
    send_to_queue(json_document)


def periodic_loop():
    # collect one sample
    try:
        record()
    except Exception as e:
        print(e)


# global
log = create_logger()


if __name__ == "__main__":
    while True:
        periodic_loop()
        sys.stdout.flush()
        time.sleep(interval_seconds)
