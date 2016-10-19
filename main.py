#!/usr/bin/env python
# -*- coding: utf-8 -*-


from AGServer import *
from DBMaintenance import *
from AGControl import *

import sys
import threading


def shutdown():
    controls.set_working_flag(False)
    GPIO.cleanup()
    sys.exit()


def main():
    # Init threads
    agc_thread = threading.Thread(target=agc, args=())
    server_thread = threading.Thread(target=server, args=())
    db_thread = threading.Thread(target=db_maintenance, args=())

    # Start threads

    agc_thread.start()
    print('Started AGControl')
    server_thread.start()
    print('Started AGC Server')
    db_thread.start()
    print('Started DB Maintenance')

    # Join threads to the main thread
    agc_thread.join()
    server_thread.join()
    db_thread.join()

    shutdown()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        shutdown()
