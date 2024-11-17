#!/usr/bin/env python

import re
import logging
import json
import time
import serial
import datetime
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb

ser = serial.Serial("/dev/ttyACM0", 9600)
mq = Mqtt('rpi4b-1.ourhouse')
MQTT_TOPIC = 'sun-chaser/weather'

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

if __name__ == '__main__':
    no2s = []
    nh3s = []
    o3s = []

    reading = {}

    while True:
        data = []
        line = ser.readline().decode('utf-8').strip()
        # print(line)
        values = line.split(':')

        if len(values) != 6:
            print(f'Invalid data: {line}')
            continue

        no2s.append(int(values[1]))
        nh3s.append(int(values[3]))
        o3s.append(int(values[5]))

        if len(no2s) >= 30 and len(nh3s) >= 30 and len(o3s) >= 30:
            reading['measurement'] = 'air_quality'
            reading['time'] = datetime.datetime.now(datetime.UTC).isoformat()
            reading['tags'] = {'sensorName': 'MICS6814', 'sensorLocation': 'OurHouse', 'sensorType': 'MICS6814'}
            reading['fields'] = {
                'no2_raw': int(sum(no2s) / len(no2s)),
                'nh3_raw': int(sum(nh3s) / len(nh3s)),
                'o3_raw': int(sum(o3s) / len(o3s))
            }
            data.append(reading)
            db_client.write_points(data, database='weather_data', retention_policy='one_year')

            for d in data:
                topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
                mq.send(topic, json.dumps(d))

            topic = MQTT_TOPIC + '/no2'
            mq.send(topic, int(sum(no2s) / len(no2s)))
            print(reading)

            no2s = []
            nh3s = []
            o3s = []
            reading = {}
            time.sleep(0.1)
