#!/usr/bin/env python3
""" The main weathermon program """

import time
import lib.conversions as conv
from lib.mqtt import Mqtt
from lib.ad import ADS1015
from lib.shtc3 import SHTC3
from lib.lps22hb import LPS22HB
from lib.anemometer import Anemometer
from lib.dht11 import DHT11

def main():
    th = SHTC3()
    pr = LPS22HB()
    an = Anemometer(5)
    dr = ADS1015()
    dh = DHT11(23)

    an.start()

    while True:
        pressure = conv.hpa_to_inhg(conv.adjust_for_altitude(pr.pressure()))
        temp1 = pr.temperature()
        temp2 = th.temperature()
        humidity = th.humidity()
        dh_humid, dh_temp = dh.readings()
        windspeed = an.windspeed()
        d_text,d_value = dr.direction()
        gust = an.gust()

        print("---[{}]---".format(time.asctime()))
        print("Pressure     : {:.2f}".format(pressure))
        print("Temperature1 : {:.2f}".format(conv.c_to_f(temp1)))
        print("Temperature2 : {:.2f}".format(conv.c_to_f(temp2)))
        print("DHT Temp     : {:.2f}".format(conv.c_to_f(dh_temp)))
        print("Humidity     : {:.2f} %".format(humidity))
        print("DHT Humidity : {:.2f} %".format(dh_humid))
        print("Wind Speed   : {:.2f} Mph".format(windspeed))
        print("Max Gust     : {:.2f} Mph".format(gust))
        print("Wind Dir     : {} | {}".format(d_text, d_value))
        print("-----------------------------\n")
        time.sleep(5)
    pass

if __name__ == "__main__":
    main()
