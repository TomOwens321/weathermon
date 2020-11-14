import asyncio
from aioambient import Client

class AmbientWeather():
    def __init__(self, api_key, app_key):
        self.client = Client(api_key, app_key)

    async def _get_current(self):
        try:
            data = await self.client.api.get_devices()
        except:
            print("Error communicating with AmbientWeather")
            return []
        return data
    
    async def _get_full_day(self, dev):
        try:
            data = await self.client.api.get_device_details(dev)
        except:
            print("Error communicating with AmbientWeather")
            return []
        return data

    def get_current(self):
        return asyncio.run(self._get_current())

    def get_full_day(self):
        current = asyncio.run(self._get_current())
        mac = current[0]['macAddress']
        return asyncio.run(self._get_full_day(mac))
