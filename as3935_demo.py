import time
import json
import RPi.GPIO as GPIO
from datetime import datetime
from lib.mqtt import Mqtt
from lib.sparkfun_qwiicas3935 import Sparkfun_QwiicAS3935_SPIDEV as AS3935
from lib.influxdb import Influxdb

INTERRUPT_PIN = 21
SPI_CHANNEL = 0

INDOOR = 0x12
OUTDOOR = 0x0E

GPIO.setmode(GPIO.BCM)
GPIO.setup(INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

event_counter = {1: 0, 4: 0, 8: 0}
event = {'distance': 100, 'energy': 0}

l_count, d_count, n_count = 0, 0, 0

db = Influxdb(host='rpi4b-1', port='8086')
db_client = db.client()
mq_topic = 'sun-chaser/lightning'
mq = Mqtt('192.168.1.10')

kaboom = []

def setup_db(client):
    client.create_database('sensors_test')
    client.create_retention_policy('oneday', '1d', '1', database='sensors_test')
    client.create_retention_policy('onemonth', '30d', '1', database='sensors_test')

def _isr(channel):
    global print_new
    time.sleep(0.002)
    interrupt = lightning.read_interrupt_register()
    if interrupt in event_counter:
        event_counter[interrupt] += 1
    else:
        print("Interrupt {} triggered".format(interrupt))

    if interrupt > 4:
        event = {}
        event['timestamp'] = time.asctime()
        event['time'] = int(time.time() * 1000000000)
        event['type_num'] = interrupt
        event['distance'] = lightning.distance_to_storm
        event['energy'] = lightning.lightning_energy
        # lightning.clear_statistics()
        kaboom.append(event)

    print_new = True
    # print("Interrupt {} triggered".format(interrupt))

def package_kabooms():
    global event_counter, n_count, d_count, l_count
    data = []
    for k in kaboom:
        reading = {'measurement': 'weathermon'}
        reading['time'] = k['time']
        reading['tags'] = {'sensorName': 'AS3935', 'sensorLocation': 'Ourhouse'}
        reading['fields'] = {
            'timestamp': k['timestamp'],
            'distance': k['distance'],
            'energy': k['energy'],
            'type': k['type_num']
        }
        data.append(reading)

    reading = {'measurement': 'weathermon'}
    reading['tags'] = {'sensorName': 'AS3935', 'sensorLocation': 'Ourhouse'}
    reading['fields'] = {
        'noise': event_counter[1],
        'disturber': event_counter[4],
        'lightning': event_counter[8]
    }
    data.append(reading)

    l_count += event_counter[8]
    d_count += event_counter[4]
    n_count += event_counter[1]

    event_counter = {1: 0, 4: 0, 8: 0}
    return data

def start():
    GPIO.add_event_detect(INTERRUPT_PIN, GPIO.RISING, callback=_isr, bouncetime=2)

def stop():
    GPIO.remove_event_detect(INTERRUPT_PIN)

def adjust_watchdog_threshold():
    global event_counter
    global lightning

    d_count = event_counter[4]
    w_dog = lightning.watchdog_threshold

    if d_count >= 20 and w_dog < 7:
        print("Increasing watchdog trigger to {}".format(w_dog + 1))
        lightning.watchdog_threshold = w_dog + 1
        lightning.calibrate()
    elif d_count <= 5 and w_dog > 2:
        print("Decreasing watchdog trigger to {}".format(w_dog - 1))
        lightning.watchdog_threshold = w_dog - 1
        lightning.calibrate()

setup_db(db_client)

lightning = AS3935(SPI_CHANNEL)
lightning.reset()

for i in range(9):
    value = lightning._read_register(i)
    print("Register {:02x} value : 0b {:08b}".format(i, value))

lightning.mask_disturber = False
lightning.indoor_outdoor = OUTDOOR
# lightning.noise_level = 2
# lightning.watchdog_threshold = 3
lightning.spike_rejection = 3
# # From calibration test w/ Arduino
lightning.tune_cap = 32
lightning.calibrate()

print("------------")
for i in range(9):
    value = lightning._read_register(i)
    print("Register {:02x} value : 0b {:08b}".format(i, value))

value = lightning._read_register(0x3a)
print("Register 3a value : 0b {:08b}".format(value))

value = lightning._read_register(0x3b)
print("Register 3b value : 0b {:08b}".format(value))

start()

print_new = True

data = []

last_day = datetime.today().day

loop_count = 0
while True:
    loop_count += 1
    if print_new:
        print("\n-------------------------")
        print("Lightning Count: {}".format(l_count))
        print("Disturber Count: {}".format(d_count))
        print("Noise Count    : {}".format(n_count))
        print("Distance       : {}".format(lightning.distance_to_storm))
        print("Energy (now)   : {}".format(lightning.lightning_energy))
        print("Noise Level    : {}".format(lightning.noise_level))
        print("Watchdog Thres : {}".format(lightning.watchdog_threshold))
        print("Spike Rejection: {}".format(lightning.spike_rejection))
        print("Kaboom Count   : {}".format(len(kaboom)))
        if len(kaboom):
            print("Last Kaboom    : {}".format(kaboom[-1]))
        print("-------------------------\n")
        print_new = False

    # clear interrupt if we missed it
    if GPIO.input(INTERRUPT_PIN):
        print("Clearing missed interrupt")
        lightning.read_interrupt_register()

    # try to auto_adjust the watchdog_threshold
    # adjust_watchdog_threshold()

    # send kabooms to Influx
    kdata = package_kabooms()
    try:
        db_client.write_points(kdata, database='sensors_test', retention_policy='oneday')
    except:
        print("Error communicating with InfluxDb. Skipping")

    print(kdata)
    mq.send(mq_topic, json.dumps(data))
    kaboom = []

    if loop_count == 10:
        print_new = True
        loop_count = 0

    current_day = datetime.today().day
    if current_day != last_day:
        l_count, d_count, n_count = 0, 0, 0
        last_day = current_day

    time.sleep(30)
