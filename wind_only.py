#!/usr/bin/env python3

import time
import json
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb
from lib.ad import ADS1015
from lib.anemometer import Anemometer

db = Influxdb(host='rpi4b-1.ourhouse', port='8086')
db_client = db.client()

MQTT_TOPIC = 'sun-chaser/weather'

def get_wind(an, dr):
    reading = {}
    windspeed = an.windspeed()
    d_text,d_value = dr.direction()
    gust = an.gust()

    reading['measurement'] = 'wind'
    reading['tags'] = {'sensorName': 'Anemometer', 'sensorLocation': 'Wellhouse', 'sensorType': 'WeatherRack'}
    reading['fields'] = {
        'windspeedmph': round(windspeed, 2),
        'windgustmph': round(gust, 2),
        'winddirtext': d_text,
        'winddir': d_value
    }

    return reading

def main():
    an = Anemometer(17)
    dr = ADS1015()
    mq = Mqtt('192.168.1.10')

    an.start()

    while True:
        data = []
        data.append(get_wind(an, dr))
        print(data)
        db_client.write_points(data, database='weather_data', retention_policy='one_year')
        for d in data:
            topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
            mq.send(topic, json.dumps(d))

        an.reset_gust()
        time.sleep(60)


    pass

if __name__ == '__main__':
    main()