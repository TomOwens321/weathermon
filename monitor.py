#!/usr/bin/env python3

import ow_only as ow
import shtc3_only as sh
import wind_only as wi
import baro_only as ba
import threading

def run_ow():
    ow.main()

def run_sh():
    sh.main()

def run_wi():
    wi.main()

def run_ba():
    ba.main()

o = threading.Thread(target=run_ow)
s = threading.Thread(target=run_sh)
w = threading.Thread(target=run_wi)
b = threading.Thread(target=run_ba)

o.start()
s.start()
w.start()
b.start()
