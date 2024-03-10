#!/usr/bin/env python3

import time
import json
import lib.conversions as conv
from datetime import datetime
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb
from lib.waveplus import WavePlus

SERIAL_NUMBER = 2930108535  # set to match my device

MQTT_TOPIC = 'sun-chaser/weather'
mq = Mqtt('rpi4b-1.ourhouse')

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

def get_readings(device):
    data = []

    try:
        device.connect()
        sensor_data = device.read()
        device.disconnect()
    except:
        return False

    print(sensor_data.sensor_data)

    # Get the humidity reading from AirThings
    reading = {}
    reading['measurement'] = 'humidity'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'AirThings', 'sensorLocation': 'Basement', 'sensorType': 'WavePlus'}
    reading['fields'] = {
        'humidity': round(sensor_data.sensor_data[0], 2)
    }
    data.append(reading)

    # Get the temperature reading from AirThings
    reading = {}
    reading['measurement'] = 'temperature'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'AirThings', 'sensorLocation': 'Basement', 'sensorType': 'WavePlus'}
    reading['fields'] = {
        'tempc': round(sensor_data.sensor_data[3], 2),
        'tempf': round(conv.c_to_f(sensor_data.sensor_data[3]),2)
    }
    data.append(reading)

    # Get the pressure reading from AirThings
    rawhg = conv.hpa_to_inhg(sensor_data.sensor_data[4])
    reading = {}
    reading['measurement'] = 'barometer'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'AirThings', 'sensorLocation': 'Basement', 'sensorType': 'WavePlus'}
    reading['fields'] = {
        'raw_inhg': round(rawhg, 2),
        'pressure': round(conv.hpa_to_inhg(conv.adjust_for_altitude(sensor_data.sensor_data[4], alt=4950)), 2)
    }
    data.append(reading)

    # Get the radon readings from AirThings
    reading = {}
    reading['measurement'] = 'radon'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'AirThings', 'sensorLocation': 'Basement', 'sensorType': 'WavePlus'}
    reading['fields'] = {
        'short_term_radon': sensor_data.sensor_data[1],
        'long_term_radon':  sensor_data.sensor_data[2],
        'short_term_radon_us': round(sensor_data.sensor_data[1] / 37.0,1),
        'long_term_radon_us':  round(sensor_data.sensor_data[2] / 37.0,1)
    }
    data.append(reading)

    # Get the CO2 readings from AirThings
    reading = {}
    reading['measurement'] = 'co2'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'AirThings', 'sensorLocation': 'Basement', 'sensorType': 'WavePlus'}
    reading['fields'] = {
        'carbon_dioxide': sensor_data.sensor_data[5]
    }
    data.append(reading)

    # Get the VOC readings from AirThings
    reading = {}
    reading['measurement'] = 'voc'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'AirThings', 'sensorLocation': 'Basement', 'sensorType': 'WavePlus'}
    reading['fields'] = {
        'voc': sensor_data.sensor_data[6]
    }
    data.append(reading)

    # Add readings to air_quality measurement
    reading = {}
    reading['measurement'] = 'air_quality'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'AirThings', 'sensorLocation': 'Basement', 'sensorType': 'WavePlus'}
    reading['fields'] = {
        'co2': sensor_data.sensor_data[5],
        'voc': sensor_data.sensor_data[6],
        'radon_short_term': sensor_data.sensor_data[1],
        'radon_long_term': sensor_data.sensor_data[2],
        'short_term_radon_us': round(sensor_data.sensor_data[1] / 37.0,1),
        'long_term_radon_us':  round(sensor_data.sensor_data[2] / 37.0,1)
    }
    data.append(reading)

    return data

def run():
    wp = WavePlus(SERIAL_NUMBER)

    while True:
        data = get_readings(wp)

        if data:
            db_client.write_points(data, database='weather_data', retention_policy='one_year')

            for d in data:
                topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
                mq.send(topic, json.dumps(d))

                print(d)

        time.sleep(180)

if __name__ == '__main__':
    run()
