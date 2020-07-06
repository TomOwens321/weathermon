"""Can be added to weathermon main or run stand-alone"""
import time
from lib.ownet import Ownet

HOSTS=['greenhousepi']
SENSORS=[]

for host in HOSTS:
    client = Ownet(host)

    for dev in client.devices:
        device = {'host': host, 'device': dev, 'type': client.read(dev, 'type')}
        SENSORS.append(device)

if SENSORS:
    print("I found {} devices".format(len(SENSORS)))
    print(SENSORS)

client = Ownet(HOSTS[0])
device = SENSORS[0]['device']
while True:
    print("Temperature: {:.2f}".format(client.read(device) * (9/5) + 32))
    time.sleep(5)
