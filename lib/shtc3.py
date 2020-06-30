#!/usr/bin/python
# -*- coding:utf-8 -*-
import ctypes

class SHTC3(object):
    def __init__(self):
        self.dll = ctypes.CDLL("./lib/SHTC3.so")
        init = self.dll.init
        init.restype = ctypes.c_int
        init.argtypes = [ctypes.c_void_p]
        init(None)

    def temperature(self):
        temperature = self.dll.SHTC3_Read_TH
        temperature.restype = ctypes.c_float
        temperature.argtypes = [ctypes.c_void_p]
        return temperature(None)

    def humidity(self):
        humidity = self.dll.SHTC3_Read_RH
        humidity.restype = ctypes.c_float
        humidity.argtypes = [ctypes.c_void_p]
        return humidity(None)

    def readings(self):
        return (self.humidity(), self.temperature())

if __name__ == "__main__":
    shtc3 = SHTC3()
    while True:
        print('Temperature = %6.2f°C , Humidity = %6.2f%%' % (shtc3.SHTC3_Read_Temperature(), shtc3.SHTC3_Read_Humidity()))
