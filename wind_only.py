#!/usr/bin/env python3

import time
import datetime
import json
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb
from lib.ad import ADS1015
from lib.anemometer import Anemometer

db = Influxdb(host='knode.ourhouse', port='8086')
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

def get_average(readings, max=50):
    avg = 0
    if len(readings) > max:
        readings.pop(0)
    if len(readings) > 0:
        avg = sum(readings) / len(readings)
    return avg

def main():
    an = Anemometer(17)
    dr = ADS1015()
    mq = Mqtt('192.168.1.10')
    wind_avg = []
    winddir_avg = []

    an.start()

    loop_count = 0
    last_day = 0
    max_daily_gust = 0.0

    wait_time = 15.0
    max_count = 600 / wait_time

    while True:
        data = []
        loop_count += 1
        wind = get_wind(an, dr)
        wind_avg.append(wind['fields']['windspeedmph'])
        winddir_avg.append(wind['fields']['winddir'])
        wind['fields']['windspdmph_avg10m'] = float(round(get_average(wind_avg, max=max_count), 2))
        wind['fields']['winddir_avg10m'] = float(round(get_average(winddir_avg, max=max_count), 2))

        today = datetime.date.today().day
        if today != last_day:
            max_daily_gust = 0.0
            last_day = today

        if wind['fields']['windgustmph'] > max_daily_gust:
            max_daily_gust = wind['fields']['windgustmph']
        
        wind['fields']['maxdailygust'] = max_daily_gust

        data.append(wind)
        print(data)
        db_client.write_points(data, database='weather_data', retention_policy='one_year')
        for d in data:
            topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
            mq.send(topic, json.dumps(d))

        if loop_count >= 600 / wait_time:
            an.reset_gust()
            # wind_avg = []
            # winddir_avg = []
            loop_count = 0
        
        time.sleep(wait_time)


    pass

if __name__ == '__main__':
    main()