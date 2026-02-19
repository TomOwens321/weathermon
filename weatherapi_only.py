#!/usr/bin/env python3

import json
import time
from lib.weatherapi import WeatherAPI
from lib.influxdb import Influxdb
from lib.mqtt import Mqtt

weather_api = WeatherAPI(zipcode='80301', aqi=True, pollen=True)

db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

mq = Mqtt('rpi4b-1.ourhouse')
MQTT_TOPIC = 'sun-chaser/weather'

cities = [
    {'name': 'Boulder, CO',     'location': '80301'},
    {'name': 'Platteville, CO', 'location': 'Platteville, CO'},
    {'name': 'Wickenburg, AZ',  'location': 'Wickenburg, AZ'},
    {'name': 'Canon City, CO',  'location': 'Canon City, CO'},
    {'name': 'Fort Morgan, CO', 'location': 'Fort Morgan, CO'},
    {'name': 'Las Cruces, NM',  'location': 'Las Cruces, NM'}
]

def json_to_influx(data, city_name):
    reading = {}
    reading['measurement'] = 'weatherapi_current'
    reading['time'] = data['current']['last_updated_epoch'] * 1000000000
    reading['tags'] = {'sensorName': 'WeatherAPI', 'sensorLocation': city_name, 'sensorType': 'Web'}
    reading['fields'] = {
        'temp_c': float(data['current']['temp_c']),
        'temp_f': float(data['current']['temp_f']),
        'is_day': int(data['current']['is_day']),
        'condition_text': data['current']['condition']['text'],
        'condition_code': int(data['current']['condition']['code']),
        'wind_mph': float(data['current']['wind_mph']),
        'wind_kph': float(data['current']['wind_kph']),
        'wind_degree': int(data['current']['wind_degree']),
        'wind_dir': data['current']['wind_dir'],
        'pressure_mb': float(data['current']['pressure_mb']),
        'pressure_in': float(data['current']['pressure_in']),
        'precip_mm': float(data['current']['precip_mm']),
        'precip_in': float(data['current']['precip_in']),
        'humidity': int(data['current']['humidity']),
        'cloud': int(data['current']['cloud']),
        'feelslike_c': float(data['current']['feelslike_c']),
        'feelslike_f': float(data['current']['feelslike_f']),
        'vis_km': float(data['current']['vis_km']),
        'vis_miles': float(data['current']['vis_miles']),
        'heatindex_c': float(data['current']['heatindex_c']),
        'heatindex_f': float(data['current']['heatindex_f']),
        'dewpoint_c': float(data['current']['dewpoint_c']),
        'dewpoint_f': float(data['current']['dewpoint_f']),
        'uv': float(data['current']['uv']),
        'gust_mph': float(data['current']['gust_mph']),
        'gust_kph': float(data['current']['gust_kph']),
        'co': float(data['current']['air_quality']['co']),
        'no2': float(data['current']['air_quality']['no2']),
        'o3': float(data['current']['air_quality']['o3']),
        'so2': float(data['current']['air_quality']['so2']),
        'pm2_5': float(data['current']['air_quality']['pm2_5']),
        'pm10': float(data['current']['air_quality']['pm10']),
        'us-epa-index': int(data['current']['air_quality']['us-epa-index']),
        'gb-defra-index': int(data['current']['air_quality']['gb-defra-index']),
        'hazel': float(data['current']['pollen']['Hazel']),
        'alder': float(data['current']['pollen']['Alder']),
        'birch': float(data['current']['pollen']['Birch']),
        'oak': float(data['current']['pollen']['Oak']),
        'grass': float(data['current']['pollen']['Grass']),
        'mugwort': float(data['current']['pollen']['Mugwort']),
        'ragweed': float(data['current']['pollen']['Ragweed'])
    }
    return reading

def main():
    while True:
        for city in cities:
            data = []
            try:
                weather_data = weather_api.get_current_weather(city['location'])
                print(f"Weather data for {city['name']}:")
                print(json.dumps(weather_data))
            except Exception as e:
                print(f"Error fetching weather data for {city['name']}: {e}")
                continue

            influx_data = json_to_influx(weather_data, city['name'])
            data.append(influx_data)
            try:
                db_client.write_points(data, database='weather_data', retention_policy='one_year')
            except Exception as e:
                print(f"Error writing weather data for {city['name']} to InfluxDB: {e}")

            try:
                mq.send(MQTT_TOPIC, json.dumps({'city': city['name'], 'weather': weather_data}), retain=True)
            except Exception as e:
                print(f"Error publishing weather data for {city['name']} to MQTT: {e}")
        time.sleep(1800)  # Sleep for 30 minutes

if __name__ == "__main__":
    main()
