#!/usr/bin/env python3

import time
import json
import lib.conversions as conv
from lib.lps22hb import LPS22HB
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb

MQTT_TOPIC = 'sun-chaser/weather'
mq = Mqtt('rpi4b-1.ourhouse')

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

def get_pressure(sensor):
    reading = {}
    pr = sensor.pressure()
    adjusted_pr = conv.adjust_for_altitude(pr, 4925)

    reading['measurement'] = 'barometer'
    reading['tags'] = {'sensorType': 'LPS22HB', 'sensorLocation': 'Wellhouse', 'sensorName': 'WH Pressure'}
    reading['fields'] = {
        'raw_hpa': round(pr, 2),
        'raw_inhg': round(conv.hpa_to_inhg(pr), 2),
        'adjusted_hpa': round(adjusted_pr, 2),
        'adjusted_inhg': round(conv.hpa_to_inhg(adjusted_pr), 2),
        'pressure': round(conv.hpa_to_inhg(adjusted_pr), 2)
    }

    return reading

def main():
    pr = LPS22HB()

    while True:
        data = []
        pressure = get_pressure(pr)
        data.append(pressure)
        print(data)
        db_client.write_points(data, database='weather_data', retention_policy='one_year')
        for d in data:
            topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
            mq.send(topic, json.dumps(d))

        time.sleep(60)

if __name__ == '__main__':
    main()
