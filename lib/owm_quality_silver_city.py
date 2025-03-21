import requests
# import json

URL = "http://api.openweathermap.org/data/2.5/air_pollution"
LAT = "32.778481"
LON = "-108.273811"
KEY = "64b25e00a7a8bb57d52de9514a983238"

# Canyon City 38.453327°N 105.240667°W
URI = URL + '?' + 'lat=' + LAT + '&lon=' + LON + '&appid=' + KEY

class OwmPollution:

    def __init__(self):
        self.URI = URI

    def get_air_quality(self):
        try:
            response = requests.get(self.URI)
        except:
            print("Error in request")
            return None
        if response.status_code == 200:
            # print(response.json())
            return response.json()
        else:
            print("Error requesting data")
            print(response.text)
            return None

if __name__ == '__main__':
    owm = OwmPollution()
    owm.get_air_quality()
