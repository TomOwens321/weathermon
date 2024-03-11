#!/usr/bin/env python3

import serial as ser
import time
import json
from datetime import datetime
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

MQTT_TOPIC = 'sun-chaser/weather'
mq = Mqtt('rpi4b-1.ourhouse')

def send_data(sensorReading):
    data = []
    reading = {}
    reading['measurement'] = 'co2'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'Smell', 'sensorLocation': 'LivingRoom', 'sensorType': 'MQ135'}
    reading['fields'] = {
        'carbon_dioxide': sensorReading
    }
    data.append(reading)

    if data:
        db_client.write_points(data, database='weather_data', retention_policy='one_year')

        for d in data:
            topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
            mq.send(topic, json.dumps(d))

def run(ser):

    start = time.time()
    maxPPM = 0.0
    while True:
        ser.flushInput()
        line = ser.readline().decode('utf-8').strip()

        try:
            ppm = float(line.split(':')[7])
        except:
            print(f'Error: {line}')
            continue

        if ppm > maxPPM:
            maxPPM = ppm
            print(line)

        if time.time() - start > 60:
            print(f'Max PPM: {maxPPM}')
            send_data(maxPPM)
            maxPPM = 0.0
            start = time.time()


if __name__ == '__main__':
    ser = ser.Serial('/dev/ttyUSB0', 9600)
    ser.timeout = 10
    ser.stopbits = 1
    ser.rtscts = True
    run(ser)
    ser.close()
