#!/usr/bin/env python3
""" The main weathermon program """

import time
import json
import lib.conversions as conv
from lib.mqtt import Mqtt
from lib.ad import ADS1015
from lib.shtc3 import SHTC3
from lib.lps22hb import LPS22HB
from lib.anemometer import Anemometer
from lib.influxdb import Influxdb
from lib.ownet import Ownet

db = Influxdb(host='rpi4b-1', port='8086')
client = db.client()

mq_topic = 'sun-chaser/testing'
ow_hosts = ['greenhousepi.ourhouse']

def setup_db(client):
    client.create_database('sensors_test')
    client.create_retention_policy('oneday', '1d', '1', database='sensors_test')
    client.create_retention_policy('onemonth', '30d', '1', database='sensors_test')

def get_pressure(sensor):
    reading = {}
    pr = sensor.pressure()
    adjusted_pr = conv.adjust_for_altitude(pr)

    reading['measurement'] = 'weathermon'
    reading['tags'] = {'sensorName': 'LPS22HB', 'sensorLocation': 'Ourhouse'}
    reading['fields'] = {
        'raw_hpa': pr,
        'raw_inhg': conv.hpa_to_inhg(pr),
        'adjusted_hpa': adjusted_pr,
        'adjusted_inhg': conv.hpa_to_inhg(adjusted_pr),
        'pressure': round(conv.hpa_to_inhg(adjusted_pr),2)
    }

    return reading

def get_temperature_and_humidity(sensor, name):
    reading = {}
    humid, temp = sensor.readings()

    reading['measurement'] = 'weathermon'
    reading['tags'] = {'sensorName': name, 'sensorLocation': 'Ourhouse'}
    reading['fields'] = {
        'tempc': temp,
        'tempf': round(conv.c_to_f(temp), 2),
        'humidity': round(humid, 2)
    }

    return reading

def get_wind(an, dr):
    reading = {}
    windspeed = an.windspeed()
    d_text,d_value = dr.direction()
    gust = an.gust()

    reading['measurement'] = 'weathermon'
    reading['tags'] = {'sensorName': 'Anemometer', 'sensorLocation': 'Ourhouse'}
    reading['fields'] = {
        'windspeed': windspeed,
        'gust': gust,
        'dir_text': d_text,
        'dir_value': d_value
    }

    return reading

def scan_1w_devices(hosts):
    sensors=[]

    for host in hosts:
        client = Ownet(host)

        for dev in client.devices:
            device = {'host': host, 'device': dev, 'type': client.read(dev, 'type')}
            sensors.append(device)

    if sensors:
        print("I found {} devices".format(len(sensors)))
        print(sensors)

    return sensors

def get_1w_temperature(device):
    reading = {}
    client = Ownet(device['host'])
    temp = client.read(device['device'])
    name = client.device_name(device['device'])

    reading['measurement'] = 'weathermon'
    reading['tags'] = {'sensorName': name, 'sensorLocation': 'Ourhouse'}
    reading['fields'] = {
        'tempc': temp,
        'tempf': round(conv.c_to_f(temp), 2)
    }

    return reading

def get_average(readings):
    avg = 0
    if len(readings) > 0:
        avg = sum(readings) / len(readings)
    return avg

def main():
    delay = 10
    retain = 600
    th = SHTC3()
    pr = LPS22HB()
    an = Anemometer(5)
    dr = ADS1015()
    mq = Mqtt('192.168.1.10')

    setup_db(client)
    an.start()
    loop_count = 0
    wind_avg = []
    owdevs = scan_1w_devices(ow_hosts)

    while True:
        loop_count += 1
        data = []

        for dev in owdevs:
            w1_temp = get_1w_temperature(dev)
            data.append(w1_temp)

        pressure = get_pressure(pr)
        data.append(pressure)

        temp_hum = get_temperature_and_humidity(th, 'SHTC3')
        data.append(temp_hum)

        wind = get_wind(an, dr)
        data.append(wind)
        wind_avg.append(wind['fields']['windspeed'])

        client.write_points(data, database='sensors_test', retention_policy='oneday')
        mq.send(mq_topic, json.dumps(data))

        if loop_count >= retain / delay:
            data[-1]['fields']['windspeed'] = get_average(wind_avg)
            client.write_points(data, database='sensors_test', retention_policy='onemonth')
            an.reset_gust()
            wind_avg = []
            loop_count = 0

        print("---[{}]---".format(time.asctime()))
        print("Pressure     : {:.2f}".format(pressure['fields']['pressure']))
        print("Temperature  : {:.2f}".format(temp_hum['fields']['tempf']))
        print("Humidity     : {:.2f} %".format(temp_hum['fields']['humidity']))
        print("Avg WindSpeed: {:.2f} Mph".format(get_average(wind_avg)))
        print("Wind Speed   : {:.2f} Mph".format(wind['fields']['windspeed']))
        print("Max Gust     : {:.2f} Mph".format(wind['fields']['gust']))
        print("Wind Dir     : {} | {}".format(wind['fields']['dir_text'], wind['fields']['dir_value']))
        print("-----------------------------\n")
        time.sleep(delay)

if __name__ == "__main__":
    main()
