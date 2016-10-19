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

    ''' sys.stdout.write(
        "\rHumidity = {0}, Temperature = {1}, Light = {2}, Fan = {3}, Autocontrol = {4}".format(*status_tuple))
    sys.stdout.write(
        '\nFunctions: \n1 - exit, \n2 - switch light(manually), \n3 - switch fan(manually), \n4 - turn on Autocontrol, \n9 - shutdown AGC.\n...  ')
    sys.stdout.flush()'''

    time.sleep(3)
    command = str(input())
    if command == '1':
        sock.close()
        sys.exit()
    if command == '2' or command == '3' or command == '4' or command == '9':
        print("Sending command", command)
        sock.send(command.encode())
    else:
        print('Wrong choice, try one more time.')
