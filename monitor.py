#!/usr/bin/env python3

import aw_only as aw
import ow_only as ow
import shtc3_only as sh
import wind_only as wi
import threading

def run_ow():
    ow.main()

def run_aw():
    aw.main()

def run_sh():
    sh.main()

def run_wi():
    wi.main()

o = threading.Thread(target=run_ow)
a = threading.Thread(target=run_aw)
s = threading.Thread(target=run_sh)
w = threading.Thread(target=run_wi)

o.start()
s.start()
w.start()
