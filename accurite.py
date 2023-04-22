#!/usr/bin/env python3

"""
Read values from Accurite remote thermometer and
send to influxdb
"""

import os
import time
import json
import subprocess
import lib.conversions as conv
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb

MQTT_TOPIC = 'sun-chaser/weather'
mq = Mqtt('rpi4b-1.ourhouse')

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

RTL_FILE = '/tmp/acc.json'

RTL_CMD = ["rtl_433",
           "-d", "0",
           "-Y", "minlevel=-29.0",
           "-f", "433.92M",
           "-s", "250k",
           "-C", "native",
           "-F", f"json:{RTL_FILE}"]

# Run the rtl_433 SDR utility
raw = subprocess.Popen(RTL_CMD)

def get_latest_reading():
    with open(RTL_FILE,'r+') as f:
        lines = [line.rstrip() for line in f]
        try:
            data = json.loads(lines[-1])
        except IndexError:
            data = None
        if data:
            f.seek(0)
            f.write('')
            f.truncate()
    return data

def proc_raw_data(raw):
    reading = {}
    reading['measurement'] = 'temperature'
    reading['tags'] = {'sensorName': 'AccuRite', 'sensorLocation': 'Greenhouse', 'sensorType': 'RTL_433'}
    # reading['time'] = raw['time']
    reading['fields'] = {
        'tempc': raw['temperature_C'],
        'tempf': round(conv.c_to_f(raw['temperature_C']), 2)
    }
    return reading

def send_mqtt(data):
    topic = f"{MQTT_TOPIC}/{data['measurement']}/{data['tags']['sensorName']}"
    mq.send(topic, json.dumps(data))

def send_influx(data):
    db_client.write_points([data], database='weather_data', retention_policy='one_year')

while True:
    data = get_latest_reading()
    if data:
        reading = proc_raw_data(data)
        send_mqtt(reading)
        send_influx(reading)
        print(reading)
    time.sleep(120)
