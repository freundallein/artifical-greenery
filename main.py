#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import sys
import threading

from package.AGControl import agc
from package.AGServer import server
from package.AGTelebot import ag_telebot
from package.DBMaintenance import db_maintenance


def shutdown():
    GPIO.cleanup()
    sys.exit()


def main():
    # Init threads
    agc_thread = threading.Thread(target=agc, args=())
    server_thread = threading.Thread(target=server, args=())
    db_thread = threading.Thread(target=db_maintenance, args=())
    tb_thread = threading.Thread(target=ag_telebot, args=())

    # Start threads

    agc_thread.start()
    print('Started AGControl')
    server_thread.start()
    print('Started AGC Server')
    db_thread.start()
    print('Started DB Maintenance')
    tb_thread.start()
    print('Started AG Telegram bot')

    # Join threads to the main thread
    agc_thread.join()
    server_thread.join()
    db_thread.join()
    tb_thread.join()

    shutdown()


if __name__ == '__main__':
    main()
