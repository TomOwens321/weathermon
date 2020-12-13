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

def get_average(readings):
    avg = 0
    if len(readings) > 0:
        avg = sum(readings) / len(readings)
    return avg

def main():
    an = Anemometer(17)
    dr = ADS1015()
    mq = Mqtt('192.168.1.10')
    wind_avg = []

    an.start()
    # let the anemometer get a few counts
    time.sleep(5)
    
    loop_count = 0
    while True:
        data = []
        loop_count += 1
        wind = get_wind(an, dr)
        wind_avg.append(wind['fields']['windspeedmph'])
        wind['fields']['windspdmph_avg10m'] = float(round(get_average(wind_avg), 2))

        data.append(wind)
        print(data)
        db_client.write_points(data, database='weather_data', retention_policy='one_year')
        for d in data:
            topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
            mq.send(topic, json.dumps(d))

        an.reset_gust()
        if loop_count >= 10:
            wind_avg = []
            loop_count = 0
        time.sleep(60)


    pass

if __name__ == '__main__':
    main()