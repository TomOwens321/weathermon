#1/usr/bin/env python3

import time
import json
from datetime import datetime
from lib.mqtt import Mqtt
from lib.owm_quality import OwmPollution
from lib.influxdb import Influxdb

owm = OwmPollution()
db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()
MQTT_TOPIC = 'sun-chaser/weather'
mq = Mqtt('rpi4b-1.ourhouse')

# list of lat/lon pairs for the cities
cities = [
    {'lat': '40.242151', 'lon': '-104.773687', 'name': 'Platteville'}, # Platteville
    {'lat': '32.778481', 'lon': '-108.273811', 'name': 'Silver City'}, # Silver City
    {'lat': '38.453327', 'lon': '-105.240667', 'name': 'Canyon City'}, # Canyon City
    {'lat': '31.566123', 'lon': '-110.274302', 'name': 'Sierra Vista'} # Sierra Vista
]

def get_owm_pollution(lat, lon):
    return owm.get_air_quality(lat, lon)

def json_to_influx(data, tags):
    reading = {}
    # print(type(data))
    aqi = data['list'][0]['main']['aqi']
    components = data['list'][0]['components']
    reading['measurement'] = 'air_quality'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    # reading['tags'] = {'sensorName': 'OpenWeatherMap', 'sensorLocation': 'Platteville', 'sensorType': 'Web'}
    reading['tags'] = tags
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
        for city in cities:
            data = []
            pollution = get_owm_pollution(city['lat'], city['lon'])
            if pollution is None:
                continue
            tags = {'sensorName': 'OpenWeatherMap' + city['name'],
                    'sensorLocation': city['name'],
                    'sensorType': 'Web'}
            data.append(json_to_influx(pollution, tags))
            db_client.write_points(data, database='weather_data', retention_policy='one_year')

            for d in data:
                    topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
                    mq.send(topic, json.dumps(d))

            print(data)
            time.sleep(5)
        time.sleep(1800)

if __name__ == '__main__':
    main()
