#!/usr/bin/env python3
import secrets
import json
import time
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb
from lib.ambientweather import AmbientWeather

MQTT_TOPIC = 'sun-chaser/weather'

MEASUREMENTS = {
    'temperature': ['tempf', 'tempc', 'feelsLike', 'dewPoint'],
    'temperaturein': ['tempinf', 'tempinc', 'feelsLikein', 'dewPointin'],
    'humidity': ['humidity'],
    'humidityin': ['humidityin'],
    'barometer': ['baromabsin', 'baromrelin'],
    'wind': ['winddir', 'winddir_avg10m', 'windspeedmph', 'windspdmph_avg10m', 'windgustmph', 'maxdailygust'],
    'solar': ['uv', 'solarradiation'],
    'rain': ['hourlyrainin', 'eventrainin', 'dailyrainin', 'weeklyrainin', 'monthlyrainin', 'yearlyrainin']
}

aw = AmbientWeather(secrets.AMBIENT_API_KEY, secrets.AMBIENT_APPLICATION_KEY)
mq = Mqtt('rpi4b-1.ourhouse')
db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

def type_adjustments(raw):
    for key in raw.keys():
        if isinstance(raw[key], int):
            raw[key] = float(raw[key])

    # Currently there are no celsius fields, let's add them
    try:
        if 'tempc' not in raw:
            raw['tempc'] = round((raw['tempf'] - 32) * (5 / 9), 1)
            raw['tempinc'] = round((raw['tempinf'] - 32) * (5 / 9), 1)
    except:
        print("Possible data corruption")
        print(raw)

    return raw

def create_influx_data(raw):
    # type adjustments
    measurements = []
    raw = type_adjustments(raw)

    for key in MEASUREMENTS:
        location = 'RoofTop'
        name = 'Ambient_Outdoor'
        measurement = key
        
        if key == 'temperaturein':
            location = 'Inside'
            measurement = 'temperature'
            name = 'Ambient_Indoor'
        
        if key == 'humidityin':
            location = 'Inside'
            measurement = 'humidity'
            name = 'Ambient_Indoor'
        
        data = {}
        fields = {}
        data['measurement'] = measurement
        data['time'] = raw['date']
        data['tags'] = {'sensorLocation': location, 'sensorType': 'AW-2000', 'sensorName': name}

        # field renaming for consistency with other products
        try:
            for field in MEASUREMENTS[key]:
                f_name = field
                if f_name == 'tempinf':
                    f_name = 'tempf'
                elif f_name == 'tempinc':
                    f_name = 'tempc'
                elif f_name == 'feelsLikein':
                    f_name = 'feelsLike'
                elif f_name == 'dewPointin':
                    f_name = 'dewPoint'
                elif f_name == 'humidityin':
                    f_name = 'humidity'
                elif f_name == 'baromabsin':
                    f_name = 'raw_inhg'
                elif f_name == 'baromrelin':
                    f_name = 'pressure'

                fields[f_name] = raw[field]
        except:
            print("Possible data corruption")
            print(raw)
            return []
        data['fields'] = fields
        measurements.append(data)
    # print(measurements)
    return measurements

def get_full_day():
    return aw.get_full_day()

def get_current():
    return aw.get_current()

def main():
    print("Running")

    readings = get_full_day()
    for reading in readings:
        data = create_influx_data(reading)
        db_client.write_points(data, database='weather_data', retention_policy='one_year')
        for d in data:
                topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
                mq.send(topic, json.dumps(d))

    while True:
        readings = get_current()
        print("Found {} readings.".format(len(readings)))
        for reading in readings:
            data = create_influx_data(reading['lastData'])
            db_client.write_points(data, database='weather_data', retention_policy='one_year')
            for d in data:
                topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
                mq.send(topic, json.dumps(d))
        
        time.sleep(60)

if __name__ == '__main__':
    main()
