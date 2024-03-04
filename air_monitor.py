"""
Read the values from the air monitor and send them to mqtt
Use 'python3 -m tinytuya wizard' to get the devices information
"""

import time
import json
import tinytuya
from datetime import datetime
from lib.mqtt import Mqtt
from lib.influxdb import Influxdb
import lib.conversions as conv

MQTT_TOPIC = 'sun-chaser/weather'
mq = Mqtt('rpi4b-1.ourhouse')

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

def get_readings(device):
    data = []

    try:
        sensor_data = device.status()
    except:
        print('Error getting sensor data')
        return False

    try:
        sensor_data['dps']['2']
        sensor_data['dps']['18']
        sensor_data['dps']['19']
        sensor_data['dps']['20']
        sensor_data['dps']['21']
        sensor_data['dps']['22']
    except:
        print(f'Error getting Air Quality data: {sensor_data}')
        return False


    # Get the Air Quality reading
    reading = {}
    reading['measurement'] = 'air_quality'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'Sniff', 'sensorLocation': 'Bedroom', 'sensorType': 'AirDetector'}
    reading['fields'] = {
        'co2': float(sensor_data['dps']['2']),
        'pm2_5': float(sensor_data['dps']['20']),
        'voc': float(sensor_data['dps']['21']),
        'hcho': float(sensor_data['dps']['22'])
    }
    data.append(reading)

    # Get the CO2 reading
    reading = {}
    reading['measurement'] = 'co2'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'Sniff', 'sensorLocation': 'Bedroom', 'sensorType': 'AirDetector'}
    reading['fields'] = {
        'carbon_dioxide': float(sensor_data['dps']['2'])
    }
    data.append(reading)

    # Get the VOC reading
    reading = {}
    reading['measurement'] = 'voc'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'Sniff', 'sensorLocation': 'Bedroom', 'sensorType': 'AirDetector'}
    reading['fields'] = {
        'voc': float(sensor_data['dps']['21'])
    }
    data.append(reading)

    # Get the CH2O reading
    reading = {}
    reading['measurement'] = 'hcho'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'Sniff', 'sensorLocation': 'Bedroom', 'sensorType': 'AirDetector'}
    reading['fields'] = {
        'formaldehyde': sensor_data['dps']['22']
    }
    data.append(reading)

    # Get the temperature reading
    reading = {}
    reading['measurement'] = 'temperature'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'Sniff', 'sensorLocation': 'Bedroom', 'sensorType': 'AirDetector'}
    reading['fields'] = {
        'tempc': float(sensor_data['dps']['18']),
        'tempf': float(conv.c_to_f(sensor_data.sensor_data['dps']['18']))
    }
    data.append(reading)

    # Get the humidity reading
    reading = {}
    reading['measurement'] = 'humidity'
    reading['time'] = datetime.utcnow().isoformat() + 'Z'
    reading['tags'] = {'sensorName': 'Sniff', 'sensorLocation': 'Bedroom', 'sensorType': 'AirDetector'}
    reading['fields'] = {
        'humidity': float(sensor_data['dps']['19'])
    }
    data.append(reading)

    return data

def _get_air_detector_device():
    # Scans the network for devices
    devs = tinytuya.deviceScan()
    dev = [d for d in devs.values() if d['name'] == 'AIR_DETECTOR'][0]
    print(dev)
    # air_mon = tinytuya.Device(dev['id'])
    air_mon = tinytuya.Device(dev_id=dev['id'],
                              address=dev['ip'],
                              local_key=dev['key'],
                              version=dev['version'])
    air_mon.set_version(3.3)
    air_mon.set_socketPersistent(False)
    return air_mon

if __name__ == "__main__":
    # Read the device information from the json file
    air_mon = _get_air_detector_device()

    while True:
        data = get_readings(air_mon)
        if data:
            db_client.write_points(data, database='weather_data', retention_policy='one_year')
            for d in data:
                topic = MQTT_TOPIC + '/' + d['measurement'] + '/' + d['tags']['sensorName']
                mq.send(topic, json.dumps(d))

                print(d)
        time.sleep(60)
