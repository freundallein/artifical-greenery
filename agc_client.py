#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import time
import threading
import os

sock = socket.socket()
try:
    sock.connect(('192.168.1.36', 14880))
    responding = True
except:
    print('Server not responding')
    responding = False

while responding:
    data = sock.recv(4096)
    # status_tuple=data.split(', ')
    os.system('clear')
    print(data)
    command = str(input())
    if command == '1':
        sock.close()
        sys.exit()
    if command == '2' or command == '3' or command == '4' or command == '9':
        print("Sending command", command)
        sock.send(command.encode())
    else:
        print('Wrong choice, try one more time.')
