#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import time

sock = socket.socket()
try:
    sock.connect(('192.168.1.36', 14885))
    responding = True
except:
    print('Server not responding')
    responding = False


while responding:
    data = sock.recv(4096)
    print(data)
    time.sleep(1.2)
    command = input('\nChoose function: \n0 - disconnect \n1 - switch lights \n2 - switch vent \n3 - status update \n4 - activate AutoControl \n888 - Shutdown AGC Server\n')
    if command == 0:
        sock.close()
        sys.exit()
    if command == 1 or command == 2 or command == 3 or command == 4 or command == 888:
        print("Sending command", command)
        sock.send(str(command))
    else:
        print('Wrong choice, try one more time.')
