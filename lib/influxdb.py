import influxdb

class Influxdb():

    def __init__(self, host='knode.ourhouse', port='8086'):
        self.host = host
        self.port = port

    def client(self):
        return influxdb.InfluxDBClient(self.host, self.port)


