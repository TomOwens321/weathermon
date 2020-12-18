#!/usr/bin/env python3
"""Can be added to weathermon main or run stand-alone"""
import time
import lib.conversions as conv
import json
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb
from lib.ownet import Ownet

HOSTS=['greenhousepi']

db = Influxdb(host='rpi4b-1.ourhouse', port='8086')
db_client = db.client()

mq = Mqtt('192.168.1.10')
mq_topic = 'sun-chaser/testing'

def scan_1w_devices(hosts, sensors):

    for host in hosts:
        client = Ownet(host)

        for dev in client.devices:
            device = {'host': host, 'device': dev, 'type': client.read(dev, 'type')}
            sensors.append(device)

    if sensors:
        print("I found {} devices".format(len(sensors)))
        print(sensors)
    else:
        print("No OneWire sensors found.")

    return sensors

def get_1w_temperature(device):
    reading = {}
    client = Ownet(device['host'])
    try:
        temp = client.read(device['device'])
    except:
        print("Error reading {}.".format(device['device']))
        return reading
    if temp > 75.0:
        return reading
    name = client.device_name(device['device'])
    location = 'Greenhouse'
    if name == 'Wellhouse':
        location = name

    reading['measurement'] = 'temperature'
    reading['tags'] = {'sensorName': name, 'sensorLocation': location, 'sensorType': device['type']}
    reading['fields'] = {
        'tempc': temp,
        'tempf': round(conv.c_to_f(temp), 2)
    }

    return reading

def main():
    while True:
        data = []
        sensors = []
        sensors = scan_1w_devices(HOSTS, sensors)
        for device in sensors:
            measurement = get_1w_temperature(device)
            print(measurement)
            data.append(measurement)
        db_client.write_points(data, database='weather_data', retention_policy='one_year')
        for d in data:
            topic = mq_topic + '/' + d['measurement'] + '/' + d['tags']['sensorName']
            mq.send(topic, json.dumps(d))

        time.sleep(60)

if __name__ == '__main__':
    main()
