""" Sends data to mqtt server """
import paho.mqtt.client as mqtt

class Mqtt(object):

    def __init__(self, host, client_id="weathermon"):
        self.host = host
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id, protocol=5)

    def send(self, topic, payload):
        try:
            self.client.connect(self.host)
            self.client.publish(topic, payload)
            self.client.disconnect()
        except:
            print("MQTT connection error with {}".format(self.host))
