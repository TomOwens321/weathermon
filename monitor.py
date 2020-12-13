#!/usr/bin/env python3

import aw_only as aw
import ow_only as ow
import shtc3_only as sh
import threading

def run_ow():
    ow.main()

def run_aw():
    aw.main()

def run_sh():
    sh.main()

o = threading.Thread(target=run_ow)
a = threading.Thread(target=run_aw)
s = threading.Thread(target=run_sh)

o.start()
a.start()
