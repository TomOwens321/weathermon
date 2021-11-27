import time
from lib.owm_quality import OwmPollution
from lib.influxdb import Influxdb

owm = OwmPollution()
db = Influxdb(host='knode.ourhouse', port='8086')
db_client = db.client()

def get_owm_pollution():
    return owm.get_air_quality()

def json_to_influx(data):
    reading = {}
    # print(type(data))
    aqi = data['list'][0]['main']['aqi']
    components = data['list'][0]['components']
    reading['measurement'] = 'air_quality'
    reading['tags'] = {'sensorName': 'OpenWeatherMap', 'sensorLocation': 'Platteville', 'sensorType': 'Web'}
    reading['fields'] = {
        'aqi': aqi,
        'co': components['co'],
        'no': components['no'],
        'no2': components['no2'],
        'o3': components['o3'],
        'so2': components['so2'],
        'pm2_5': components['pm2_5'],
        'pm10': components['pm10'],
        'nh3': components['nh3']
    }
    # reading['timestamp'] = data['list'][0]['dt'] * 1000000000
    return reading

def main():
    while True:
        data = []
        pollution = get_owm_pollution()
        data.append(json_to_influx(pollution))
        db_client.write_points(data, database='weather_data', retention_policy='one_year')
        print(data)
        time.sleep(1800)

if __name__ == '__main__':
    main()
