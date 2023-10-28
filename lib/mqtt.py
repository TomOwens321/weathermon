""" Sends data to mqtt server """
from paho.mqtt.client import Client

class Mqtt(object):

    def __init__(self, host):
        self.host = host
        self.client = Client(client_id="weathermon", protocol=5)

    def send(self, topic, payload):
        try:
            self.client.connect(self.host)
            self.client.publish(topic, payload)
            self.client.disconnect()
        except:
            print("MQTT connection error with {}".format(self.host))
