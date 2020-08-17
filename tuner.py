#!/usr/bin/env python3

import time
from lib.sparkfun_qwiicas3935 import Sparkfun_QwiicAS3935_SPIDEV as AS3935

SPI_CHANNEL = 0
board = AS3935(SPI_CHANNEL)

DELAY_TIME = 30

board.reset()

for c in range(16):
    board.reset()
    board.tune_cap = c * 8
    print("Setting tune cap to {} pF.".format(board.tune_cap))
    board.display_oscillator(True, 3)
    time.sleep(DELAY_TIME)

board.display_oscillator(False, 3)
board.reset()