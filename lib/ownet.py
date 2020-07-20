""" Get and set data from 1-Wire devices """

import pyownet

class Ownet(object):

    def __init__(self, host='localhost'):
        self.host = host
        self.devices = self.device_scan()

    def device_scan(self):
        devices = []

        try:
            client = self._connect()
            devices = client.dir('/uncached')
        except:
            print("Ow Connect error with {}".format(self.host))

        return devices

    def device_name(self, device):
        return device.rstrip('/').split('/')[-1]

    def read(self, device, field='temperature'):
        value = False

        try:
            client = self._connect()
            value = client.read(device + field)
        except:
            print("Ow Connect error with {}".format(self.host))

        # pyownet returns all reads as a byte array
        # this will return numbers as floats and strings as strings
        try:
            return float(value)
        except:
            return value.decode('utf-8')

    def dir(self, device):
        client = self._connect()
        return client.dir(device)

    def _connect(self):
        conn = False
        try:
            conn = pyownet.protocol.proxy(self.host)
        except:
            print("Can not establish OwNet connection with {}".format(self.host))
        return conn
