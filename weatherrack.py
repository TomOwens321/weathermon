#!/usr/bin/env python3

import re
import json
import serial
import datetime
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb

ser = serial.Serial("/dev/ttyUSB0", 9600)
MQTT_TOPIC = 'sun-chaser/weather'
db = Influxdb(host='knode.ourhouse', port='8086')
dbClient = db.client()

def procSpeed(line, speeds):
    # print("Speed line:", line)
    speed = re.findall("\d+.\d+", line)
    speeds.append(float(speed[0]))
    # print(speed[0])

def procDir(line, directions):
    # print("Direction line:", line)
    direction = re.findall("\d+.\d+", line)
    directions.append(float(direction[1]))
    # print(direction[1])

def directionText(dir):
    if (dir > 347.75 and dir < 12.25): return " N "
    elif (dir > 12.25 and dir < 34.75): return "NNE"
    elif (dir > 34.75 and dir < 57.25): return " NE"
    elif (dir > 57.25 and dir < 79.75): return "ENE"
    elif (dir > 79.75 and dir < 102.25): return " E "
    elif (dir > 102.25 and dir < 124.75): return "ESE"
    elif (dir > 124.75 and dir < 147.25): return " SE"
    elif (dir > 147.25 and dir < 169.75): return "SSE"
    elif (dir > 169.75 and dir < 192.25): return " S "
    elif (dir > 192.25 and dir < 214.75): return "SSW"
    elif (dir > 214.75 and dir < 237.25): return " SW"
    elif (dir > 237.25 and dir < 259.75): return "WSW"
    elif (dir > 259.75 and dir < 282.25): return " W "
    elif (dir > 282.25 and dir < 304.75): return "WNW"
    elif (dir > 304.75 and dir < 327.25): return " NW"
    elif (dir > 327.25 and dir < 347.75): return "NNW"
    else: return "UNK"


def procReadings(speeds, directions):
    reading = {}
    direction = round(sum(directions) / float(len(directions)), 2)
    speed = round(sum(speeds) / float(len(speeds)), 2)
    gust = round(max(speeds), 2)
    reading['measurement'] = 'wind'
    reading['tags'] = {'sensorName': 'Anemometer', 'sensorLocation': 'Wellhouse', 'sensorType': 'WeatherRack'}
    reading['fields'] = {
        'windspeedmph': speed,
        'windgustmph': gust,
        'winddir': direction,
        'winddirtext': directionText(direction),
    }

    return reading

def main():
    speeds = []
    directions = []
    speedAvg = []
    dirAvg = []
    lastDay = 0
    maxDailyGust = 0.0
    mq = Mqtt('rpi4b-1.ourhouse')

    while True:
        line = ser.readline().decode('utf-8')
        if 'Speed' in line:
            procSpeed(line, speeds)
        elif 'Direction' in line:
            procDir(line, directions)

        if len(speeds) >= 60:
            data = []

            # process the speed and direction readings
            reading = procReadings(speeds=speeds, directions=directions)
            reading['time'] = datetime.datetime.utcnow().isoformat() + 'Z'

            # reset the daily readings
            today = datetime.date.today().day
            if today != lastDay:
                print("Resetting values for a new day")
                maxDailyGust = 0.0
                lastDay = today

            if reading['fields']['windgustmph'] >= maxDailyGust:
                maxDailyGust = reading['fields']['windgustmph']

            reading['fields']['maxdailygust'] = maxDailyGust

            speedAvg.append(reading['fields']['windspeedmph'])
            if len(speedAvg) > 10:
                speedAvg.pop(0)
            reading['fields']['windspdmph_avg10m'] = round(sum(speedAvg) / float(len(speedAvg)), 2)

            dirAvg.append(reading['fields']['winddir'])
            if len(dirAvg) > 10:
                dirAvg.pop(0)
            reading['fields']['winddir_avg10m'] = round(sum(dirAvg) / float(len(dirAvg)), 2)

            data.append(reading)

            # send to influx db
            dbClient.write_points(data, database='weather_data', retention_policy='one_year')

            # send to mqtt
            for d in data:
                topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
                mq.send(topic, json.dumps(d))

            print(data)
            speeds = []
            directions = []

if __name__ == '__main__':
  main()