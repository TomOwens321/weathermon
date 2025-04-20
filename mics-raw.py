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

BASE = 1024.0

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

def coPPM(reading):
    ratio = reading / BASE
    return pow(ratio, -1.177) * 4.4638

def no2PPM(reading):
    ratio = reading / BASE
    return pow(ratio, 0.9979) * 0.1516

def nh3PPM(reading):
    ratio = reading / BASE
    return (pow(ratio, -1.903) * 0.6151) / 1000

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
                'o3_raw': int(sum(o3s) / len(o3s)),
                'no2': round((no2PPM(sum(no2s) / len(no2s)) * 100), 2),
                'nh3': round(nh3PPM(sum(nh3s) / len(nh3s)), 2),
                'co': round(coPPM(sum(o3s) / len(o3s)), 2),
            }
            data.append(reading)
            db_client.write_points(data, database='weather_data', retention_policy='one_year')

            for d in data:
                topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
                mq.send(topic, json.dumps(d))

            topic = MQTT_TOPIC + '/coppm'
            coppm = coPPM(int(sum(o3s) / len(o3s)))
            print(f'CO: {coppm:.2f} ppm')
            mq.send(topic, coppm)

            topic = MQTT_TOPIC + '/no2ppm'
            no2ppm = coPPM(int(sum(no2s) / len(no2s)))
            print(f'NO2: {no2ppm:.2f} ppm')
            mq.send(topic, no2ppm)

            topic = MQTT_TOPIC + '/nh3ppm'
            nh3ppm = nh3PPM(int(sum(nh3s) / len(nh3s)))
            print(f'NH3: {nh3ppm:.2f} ppm')
            mq.send(topic, nh3ppm)

            print(reading)

            no2s = []
            nh3s = []
            o3s = []
            reading = {}
            time.sleep(0.1)

# conversions found at https://github.com/eNBeWe/MiCS6814-I2C-Library/blob/master/src/MiCS6814-I2C.cpp
