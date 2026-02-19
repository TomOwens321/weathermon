import requests
import secrets

class WeatherAPI:
    def __init__(self, zipcode, aqi=True, pollen=True):
        self.api_key = secrets.WEATHERAPI_KEY
        self.zipcode = zipcode
        self.aqi = aqi
        self.pollen = pollen

    def get_current_weather(self, location):
        url = f"http://api.weatherapi.com/v1/current.json?key={self.api_key}&q={location}"
        if self.aqi:
            url += "&aqi=yes"
        if self.pollen:
            url += "&pollen=yes"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching weather data: {response.status_code} - {response.text}")