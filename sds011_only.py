#!/usr/bin/env python3
import json
from datetime import datetime
from sds011 import SDS011
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb

PORT = "/dev/ttyUSB0"
RATE = 10
MQTT_TOPIC = 'sun-chaser/weather'
mq = Mqtt('rpi4b-1.ourhouse')

sds = SDS011(port=PORT, rate=RATE, use_database=True)
sds.set_working_period(rate=RATE)
print(sds)

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

log_columns = ["timestamp", "pm2.5", "pm10", "device_id"]

def get_measurement():
    reading = {}

    measurement = sds.read_measurement()
    values = [str(measurement.get(key)) for key in log_columns]

    reading['measurement'] = 'air_quality'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'SDS011', 'sensorLocation': 'OurHouse', 'sensorType': 'SDS011'}
    reading['fields'] = {
        'pm2_5': float(values[1]),
        'pm10': float(values[2])
    }
    return reading

def run():
    while True:
        data = []
        reading = get_measurement()
        data.append(reading)
        db_client.write_points(data, database='weather_data', retention_policy='one_year')

        for d in data:
                topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
                mq.send(topic, json.dumps(d))

        print(reading)

if __name__ == '__main__':
    run()
