#!/usr/bin/env python3
import time
from sds011 import SDS011
from lib.influxdb import Influxdb

PORT = "/dev/ttyUSB0"
RATE = 10

sds = SDS011(port=PORT, rate=RATE, use_database=False)
sds.set_working_period(rate=RATE)
print(sds)

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

log_columns = ["timestamp", "pm2.5", "pm10", "device_id"]

def get_measurement():
    reading = {}

    measurement = sds.read_measurement()
    values = [str(measurement.get(key)) for key in log_columns]

    reading['measurement'] = 'air_quality'
    reading['tags'] = {'sensorName': 'SDS011', 'sensorLocation': 'OurHouse', 'sensorType': 'SDS011'}
    reading['fields'] = {
        'pm2_5': float(values[1]),
        'pm10': float(values[2])
    }
    return reading

def run():    
    while True:
        data = []
        reading = get_measurement()
        data.append(reading)
        db_client.write_points(data, database='weather_data', retention_policy='one_year')
        print(reading)

if __name__ == '__main__':
    run()
