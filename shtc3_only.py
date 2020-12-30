#!/usr/bin/env python3
import time
import json
import lib.conversions as conv
from lib.mqtt import Mqtt
from lib.shtc3 import SHTC3
from lib.influxdb import Influxdb

MQTT_TOPIC = 'sun-chaser/weather'
mq = Mqtt('192.168.1.10')

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

def get_temperature_and_humidity(sensor, name):
    data = []
    humid, temp = sensor.readings()

    reading = {}
    reading['measurement'] = 'temperature'
    reading['tags'] = {'sensorName': name, 'sensorLocation': 'Wellhouse', 'sensorType': 'SHTC3'}
    reading['fields'] = {
        'tempc': temp,
        'tempf': round(conv.c_to_f(temp), 2)
    }

    data.append(reading)

    reading = {}
    reading['measurement'] = 'humidity'
    reading['tags'] = {'sensorName': name, 'sensorLocation': 'Wellhouse', 'sensorType': 'SHTC3'}
    reading['fields'] = {
        'humidity': round(humid, 2)
    }

    data.append(reading)

    return data

def main():
    th = SHTC3()
    
    while True:
        data = get_temperature_and_humidity(th, 'PiBoxInside')
        print(data)
        db_client.write_points(data, database='weather_data', retention_policy='one_year')
        for d in data:
            topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
            mq.send(topic, json.dumps(d))

        time.sleep(60)

if __name__ == '__main__':
    main()
