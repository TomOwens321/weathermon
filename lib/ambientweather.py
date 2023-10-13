import requests
import secrets

class AmbientWeather():
    def __init__(self):
        self.api_key = secrets.AMBIENT_API_KEY
        self.app_key = secrets.AMBIENT_APPLICATION_KEY
        self.url = secrets.AMBIENT_ENDPOINT
        self.dev = secrets.MAC_ADDRESS

    def get_current(self):
        data = {}
        try:
            url = f'{self.url}/devices?applicationKey={self.app_key}&apiKey={self.api_key}'
            resp = requests.get(url, timeout=1)
            data = resp.json()
        except Exception as exc:
            print(f'Failed communicating with {self.url}')
        return data

    def get_full_day(self):
        data = {}
        try:
            url = f'{self.url}/devices/{self.dev}?applicationKey={self.app_key}&apiKey={self.api_key}'
            resp = requests.get(url, timeout=2)
            data = resp.json()
        except Exception as exc:
            print(f'Failed communicating with {self.url}')
        return data
