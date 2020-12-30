#!/usr/bin/env python3
import secrets
import json
import time
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb
from lib.ambientweather import AmbientWeather

MQTT_TOPIC = 'sun-chaser/weather/ambientweather'

aw = AmbientWeather(secrets.AMBIENT_API_KEY, secrets.AMBIENT_APPLICATION_KEY)
mq = Mqtt('192.168.1.10')
db = Influxdb(host='knode', port='8086')
db_client = db.client()

def type_adjustments(raw):
    for key in raw.keys():
        if isinstance(raw[key], int):
            raw[key] = float(raw[key])

    # Currently there are no celsius fields, let's add them
    if 'tempc' not in raw:
        raw['tempc'] = round((raw['tempf'] - 32) * (5 / 9), 1)
        raw['tempinc'] = round((raw['tempinf'] - 32) * (5 / 9), 1)
    return raw

def create_influx_data(raw):
    # type adjustments
    raw = type_adjustments(raw)

    data = {}
    data['measurement'] = 'weathermon'
    data['time'] = raw['date']
    data['tags'] = {'sensorLocation': 'Ourhouse', 'sensorName': 'AW-2000'}
    data['fields'] = raw
    return data

def get_full_day():
    details = aw.get_full_day()
    for detail in details:
        data = []
        data.append(create_influx_data(detail))
        db_client.write_points(data, database='sensors_test', retention_policy='oneday')

def main():
    print("Running")

    while True:
        readings = aw.get_current()
        
        for reading in readings:
            data = []
            data.append(create_influx_data(reading['lastData']))
            mq.send(MQTT_TOPIC, json.dumps(data[0]))
            db_client.write_points(data, database='sensors_test', retention_policy='oneday')

        time.sleep(120)

    print("Finished")

if __name__ == '__main__':
    main()
