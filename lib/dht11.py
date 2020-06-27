import Adafruit_DHT as DHT

class DHT11():

    def __init__(self, pin=23):
        self.pin = pin
        self.sensor = DHT.DHT11

    def readings(self):
        humidity, temperature = DHT.read_retry(self.sensor, self.pin)
        return humidity, temperature

