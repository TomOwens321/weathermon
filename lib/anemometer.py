
import time
import RPi.GPIO as GPIO

class Anemometer():
    
    WIND_FACTOR = 1.492

    def __init__(self, pin=25):
        self.anemometer_pin = pin
        self.last_time = 0
        self.delta = 0
        self.gust_delta = 0xffff

        self.setup()

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.anemometer_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _isr(self, channel):
        now_time = time.time()
        self.delta = now_time - self.last_time
        if self.delta < self.gust_delta:
            self.gust_delta = self.delta
        self.last_time = now_time
        # print("Anemometer trigger event")

    def start(self):
        GPIO.add_event_detect(self.anemometer_pin, GPIO.RISING, callback=self._isr)

    def stop(self):
        GPIO.remove_event_detect(self.anemometer_pin)

    def windspeed(self):
        mph = 0.0
        if self.delta > 5:
            self.delta = 0
        if self.delta > 0:
           mph = ( 1 / self.delta ) * self.WIND_FACTOR
        return mph

    def gust(self):
        mph = 0.0
        if self.gust_delta < 10.0:
            mph =  ( 1 / self.gust_delta ) * self.WIND_FACTOR
        return mph

    def reset_gust(self):
        self.gust_delta = 0xffff

