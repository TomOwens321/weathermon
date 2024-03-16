#!/usr/bin/env python3

import serial as ser
import time
import json
import lib.conversions as conv
from datetime import datetime
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

MQTT_TOPIC = 'sun-chaser/weather'
# MQTT_TEMPERATURE_TOPIC = MQTT_TOPIC + '/temperature/Ambient_Outdoor'
# MQTT_HUMIDITY_TOPIC = MQTT_TOPIC + '/humidity/Ambient_Outdoor'

mq = Mqtt('rpi4b-1.ourhouse')
mq_listen = Mqtt('rpi4b-1.ourhouse', client_id='weather_listener')

temperature = 20.0
humidity = 50.0

def send_data(sensorReading, temperature, humidity):
    data = []

    # Get adjusted CO2 PPM reading
    reading = {}
    reading['measurement'] = 'co2'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'Smell', 'sensorLocation': 'LivingRoom', 'sensorType': 'MQ135'}
    reading['fields'] = {
        'carbon_dioxide': sensorReading
    }
    data.append(reading)

    # Get temperature reading
    reading = {}
    reading['measurement'] = 'temperature'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'Smell', 'sensorLocation': 'LivingRoom', 'sensorType': 'DHT11'}
    reading['fields'] = {
        'tempc': temperature,
        'tempf': round(conv.c_to_f(temperature), 2)
    }
    data.append(reading)

    # Get humidity reading
    reading = {}
    reading['measurement'] = 'humidity'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'Smell', 'sensorLocation': 'LivingRoom', 'sensorType': 'DHT11'}
    reading['fields'] = {
        'humidity': humidity
    }
    data.append(reading)

    if data:
        db_client.write_points(data, database='weather_data', retention_policy='one_year')

        for d in data:
            topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
            mq.send(topic, json.dumps(d))

def run(ser):
    start = time.time()
    maxPPM = 0.0
    while True:
        ser.flushInput()
        line = ser.readline().decode('utf-8').strip()

        try:
            resistance = float(line.split(':')[5])
            rzero = float(line.split(':')[3])
            ppm = float(line.split(':')[9])
            temperature = round(float(line.split(':')[11]), 2)
            humidity = round(float(line.split(':')[13]), 2)
            # ppm = round(conv.get_corrected_pm(temperature, humidity, resistance, rzero), 2)
        except:
            print(f'Error: {line}')
            continue

        if ppm > maxPPM:
            maxPPM = ppm
            print(line)
            print(f'Temperature: {temperature} | Humidity {humidity} | Resistance: {resistance} | Rzero: {rzero}')

        if time.time() - start > 60:
            print(f'Max PPM: {maxPPM}')
            send_data(maxPPM, temperature, humidity)
            maxPPM = 0.0
            start = time.time()

# def start_mqtt_listener():
#     mq_listen.client.connect('rpi4b-1.ourhouse')
#     mq_listen.client.on_connect = on_connect
#     mq_listen.client.on_message = on_message
#     mq_listen.client.loop_start()

# def on_connect(client, userdata, flags, rc, properties=None):
#     print(f'Connected with result code {rc}')
#     if rc == 0:
#         print(f'Subscribing to {MQTT_TEMPERATURE_TOPIC}')
#         print(f'Subscribing to {MQTT_HUMIDITY_TOPIC}')
#         client.subscribe([(MQTT_TEMPERATURE_TOPIC, 0), (MQTT_HUMIDITY_TOPIC, 0)])
#     else:
#         print('Connection failed')

# def on_message(client, userdata, message):
#     global temperature, humidity
#     print(f'{message.topic}: {message.payload}')
#     msg = json.loads(message.payload)
#     if message.topic == MQTT_TEMPERATURE_TOPIC:
#         temperature = float(msg['fields']['tempc'])
#     elif message.topic == MQTT_HUMIDITY_TOPIC:
#         humidity = float(msg['fields']['humidity'])
#     else:
#         print(f'Unknown topic: {message.topic}')
#         return

if __name__ == '__main__':
    # start_mqtt_listener()
    ser = ser.Serial('/dev/ttyUSB0', 9600)
    ser.timeout = 10
    ser.stopbits = 1
    ser.rtscts = True
    run(ser)
    ser.close()
