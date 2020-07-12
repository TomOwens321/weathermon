import time
import RPi.GPIO as GPIO
from lib.spidev_as3935 import AS3935

INTERRUPT_PIN = 21
SPI_CHANNEL = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

event_counter = {1: 0, 4: 0, 8: 0}
event = {'distance': 100, 'energy': 0}
kaboom = []

def _isr(channel):
    time.sleep(0.02)
    interrupt = lightning.interrupt()
    if interrupt in event_counter:
        event_counter[interrupt] += 1
    else:
        print("Interrupt {} triggered".format(interrupt))

    if interrupt >= 4:
        event = {}
        event['timestamp'] = time.asctime()
        event['type_num'] = interrupt
        event['distance'] = lightning.distance
        event['energy'] = lightning.energy
        kaboom.append(event)

    if len(kaboom) > 10:
        kaboom.pop(0)

    print_new = True
    # print("Interrupt {} triggered".format(interrupt))


def start():
    GPIO.add_event_detect(INTERRUPT_PIN, GPIO.RISING, callback=_isr, bouncetime=2)

def stop():
    GPIO.remove_event_detect(INTERRUPT_PIN)

lightning = AS3935(SPI_CHANNEL)
lightning.set_defaults()
lightning.mask_disturbers(True)
start()


loop_count = 0
print_new = True

while True:
    loop_count += 1
    if print_new:
        print("\n-------------------------")
        print("Lightning Count: {}".format(event_counter[8]))
        print("Disturber Count: {}".format(event_counter[4]))
        print("Noise Count    : {}".format(event_counter[1]))
        print("Distance       : {}".format(event['distance']))
        print("Energy (now)   : {}".format(lightning.energy))
        print("Energy (stored): {}".format(event['energy']))
        print("Interrupt State: {}".format(GPIO.input(INTERRUPT_PIN)))
        print("Kaboom Count   : {}".format(len(kaboom)))
        if len(kaboom):
            print("Last Kaboom    : {}".format(kaboom[-1]))
        print_new = False

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
