import influxdb

class Influxdb():

    def __init__(self, host='rpi4b-1.ourhouse', port='8086'):
        self.host = host
        self.port = port

    def client(self):
        return influxdb.InfluxDBClient(self.host, self.port)


