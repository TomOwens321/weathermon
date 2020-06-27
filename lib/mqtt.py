""" Sends data to mqtt server """
from paho.mqtt.client import Client

class Mqtt(object):

    def __init__(self, host):
        self.host = host
        self.client = Client()

    def send(self, topic, payload):
        try:
            self.client.connect(self.host)
            self.client.disconnect()
        except:
            print("MQTT connection error with {}".format(self.host))

