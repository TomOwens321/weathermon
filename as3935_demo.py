import time
import RPi.GPIO as GPIO
from lib.spidev_as3935 import AS3935

INTERRUPT_PIN = 21
SPI_CHANNEL = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

events = {1: 0,
          4: 0,
          8: 0,
          'distance': 100,
          'energy': 0
          }

def _isr(channel):
    time.sleep(0.02)
    interrupt = lightning.interrupt()
    if interrupt in events:
        events[interrupt] += 1
    else:
        print("Interrupt {} triggered".format(interrupt))

    if interrupt == 8:
        events['distance'] = lightning.distance
        events['energy'] = lightning.energy
    # print("Interrupt {} triggered".format(interrupt))


def start():
    GPIO.add_event_detect(INTERRUPT_PIN, GPIO.RISING, callback=_isr)

def stop():
    GPIO.remove_event_detect(INTERRUPT_PIN)

lightning = AS3935(SPI_CHANNEL)
lightning.set_defaults()

start()


loop_count = 0

while True:
    loop_count += 1
    print("\n-------------------------")
    print("Lightning Count: {}".format(events[8]))
    print("Disturber Count: {}".format(events[4]))
    print("Noise Count    : {}".format(events[1]))
    print("Distance       : {}".format(events['distance']))
    print("Energy (now)   : {}".format(lightning.energy))
    print("Energy (stored): {}".format(events['energy']))
    print("Interrupt State: {}".format(GPIO.input(INTERRUPT_PIN)))

    # clear interrupt if we missed it
    if GPIO.input(INTERRUPT_PIN):
        print("Clearing missed interrupt")
        lightning.interrupt()

    # if not loop_count % 5:
    #     print("Masking disturbers")
    #     lightning.mask_disturbers(True)
    # if not loop_count % 7:
    #     print("Unasking disturbers")
    #     lightning.mask_disturbers(False)

    time.sleep(30)