
import time
import threading
import RPi.GPIO as GPIO

class Anemometer():

    WIND_FACTOR = 1.492

    def __init__(self, pin=25):
        self.anemometer_pin = pin
        self.pulse_count = 0
        self.speed = 0.0
        self.max_gust = 0.0
        self.last_reading_time = time.time()
        self.last_time = 0
        self.thread = threading.Thread(target=self.set_speeds)

        self.setup()

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.anemometer_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _isr(self, channel):
        self.pulse_count += 1

    def set_speeds(self):
        while True:
            self.speed = self.get_windspeed()
            if self.speed > self.max_gust:
                self.max_gust = self.speed
            time.sleep(10)

    def start(self):
        GPIO.add_event_detect(self.anemometer_pin, GPIO.RISING, callback=self._isr)
        self.thread.start()

    def stop(self):
        GPIO.remove_event_detect(self.anemometer_pin)

    def rpm(self):
        rpm = 0.0
        now_time = time.time()
        if self.pulse_count > 0:
            rpm = (self.pulse_count / (now_time - self.last_reading_time))  * 30
        return rpm

    def get_windspeed(self):
        now_time = time.time()
        time_delta = now_time - self.last_reading_time
        mph = (self.pulse_count / time_delta) * self.WIND_FACTOR
        self.pulse_count = 0
        self.last_reading_time = now_time
        return mph

    def windspeed(self):
        return self.speed

    def instant_windspeed(self):
        mph = 0.0
        if self.delta > 5:
            self.delta = 0
        if self.delta > 0:
           mph = ( 1 / self.delta ) * self.WIND_FACTOR
        return mph

    def gust(self):
        return self.max_gust

    def reset_gust(self):
        self.max_gust = 0.0

