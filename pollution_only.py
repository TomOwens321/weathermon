#1/usr/bin/env python3

import time
import json
from lib.mqtt import Mqtt
from lib.owm_quality import OwmPollution
from lib.influxdb import Influxdb

owm = OwmPollution()
db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()
MQTT_TOPIC = 'sun-chaser/weather'
mq = Mqtt('rpi4b-1.ourhouse')

def get_owm_pollution():
    return owm.get_air_quality()

def json_to_influx(data):
    reading = {}
    # print(type(data))
    aqi = data['list'][0]['main']['aqi']
    components = data['list'][0]['components']
    reading['measurement'] = 'air_quality'
    reading['tags'] = {'sensorName': 'OpenWeatherMap', 'sensorLocation': 'Platteville', 'sensorType': 'Web'}
    reading['fields'] = {
        'aqi': aqi,
        'co': float(components['co']),
        'no': float(components['no']),
        'no2': float(components['no2']),
        'o3': float(components['o3']),
        'so2': float(components['so2']),
        'pm2_5': float(components['pm2_5']),
        'pm10': float(components['pm10']),
        'nh3': float(components['nh3'])
    }
    # reading['timestamp'] = data['list'][0]['dt'] * 1000000000
    return reading

def main():
    while True:
        data = []
        pollution = get_owm_pollution()
        data.append(json_to_influx(pollution))
        db_client.write_points(data, database='weather_data', retention_policy='one_year')

        for d in data:
                topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
                mq.send(topic, json.dumps(d))

        print(data)
        time.sleep(1800)

if __name__ == '__main__':
    main()
