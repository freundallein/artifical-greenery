#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import os

from package.AGControl import agc, shutdown
from package.AGServer import server
from package.AGTelebot import ag_telebot
from package.DBMaintenance import db_maintenance




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



if __name__ == '__main__':
    if not os.path.exists('log'):
        os.makedirs('log')
    if not os.path.exists('img'):
        os.makedirs('img')
    try:
        main()
        shutdown()
    except KeyboardInterrupt:
        shutdown()
