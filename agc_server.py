#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import Adafruit_DHT
import psycopg2

import sys
import time
import threading
import socket
import logging

# Initialize GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

light_pin = 7  # Set BOARD rpi.pin for illumination
#  pump_pin = 3 #  Set BOARD rpi.pin for irrigation
fan_pin = 5  # Set BOARD rpi.pin for ventilation

# Set pins for output
# GPIO.setup(pump_pin, GPIO.OUT)
GPIO.setup(fan_pin, GPIO.OUT)
GPIO.setup(light_pin, GPIO.OUT)

GPIO.output(light_pin, True)
GPIO.output(fan_pin, True)

# Sensor and GPIO.input_pin initialize
sensor = Adafruit_DHT.DHT11
DHT_pin = '14'  # Means BCM.GPIO14 (GPIO.BOARD - 8)

logging.basicConfig(filename='agc_server.log',
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


class Status():

    def __init__(self):
        self.humidity, self.temperature = Adafruit_DHT.read_retry(sensor, DHT_pin)

    def setHumidity(self):
        self.humidity = Adafruit_DHT.read_retry(sensor, DHT_pin)[0]

    def setTemperature(self):
        self.temperature = Adafruit_DHT.read_retry(sensor, DHT_pin)[1]

    def getHumidity(self):
        return self.humidity

    def getTemperature(self):
        return self.temperature

    def checkServerTime(self):
        return time.strftime('%H:%M')


class Controls():

    def __init__(self):
        self.light_status = False
        self.fan_status = False
        self.working_flag = True
        self.autocontrol_flag = int(config['autocontrol'])

    def setLightStatus(self, flag):
        self.light_status = bool(flag)

    def setFanStatus(self, flag):
        self.fan_status = bool(flag)

    def setAutocontrolFlag(self, flag):
        self.autocontrol_flag = bool(flag)

    def setWorkingFlag(self, flag):
        self.working_flag = bool(flag)

    def getLightStatus(self):
        return self.light_status

    def getFanStatus(self):
        return self.fan_status

    def getAutocontrolFlag(self):
        return self.autocontrol_flag

    def getWorkingFlag(self):
        return self.working_flag


def reading_config():
    try:
        config_file = open('agc.conf', 'r')
        config_line = config_file.read().split('\n')
        config = {}
        for i in range(len(config_line)):
            if ('[' in config_line[i]) or (not config_line[i]):
                pass
            else:
                parts = config_line[i].split(' = ')
                config[parts[0]] = parts[1]
        config_file.close()
        return config
    except IOError as err:
        print(err, '\n Config not found')
        print('Making config...')
        logging.warning(err)
        logging.warning('Config not found!')
        logging.info('Making config.')
        file = open("agc.conf", "w+")
        file.write('[General]' + '\n')
        file.write('max_temperature = 30' + '\n')
        file.write('max_humidity = 50' + '\n')
        file.write('morning_time = 08:00' + '\n')
        file.write('evening_time = 21:00' + '\n')
        file.write('autocontrol = 1' + '\n')
        file.close()
        print('Config complete. Please, restart.')
        logging.info('Config complete')
        sys.exit()


# Making start conditions
config = reading_config()

status = Status()
controls = Controls()


# Function for mechs control
def agc(status, controls, config):
    while controls.getWorkingFlag():
        status.setHumidity()
        status.setTemperature()
        status.checkServerTime()
        if controls.getAutocontrolFlag():
            automaticalControl(status, controls, config)
        time.sleep(0.2)


def automaticalControl(status, controls, config):
    if status.getTemperature() > config['max_temperature'] or status.getHumidity() > config['max_humidity']:
        logging.warning('High temperature or humidity')
        logging.warning(status.getTemperature())
        logging.warning(status.getHumidity())
        switching_fan(True, controls)
    elif status.getTemperature() <= (int(config['max_temperature']) - 2):
        switching_fan(False, controls)

    if config['morning_time'] <= status.checkServerTime() <= config['evening_time']:
        switching_light(True, controls)
    else:
        switching_light(False, controls)


def switching_light(boolean, controls):
    if boolean:
        GPIO.output(light_pin, False)
        controls.setLightStatus(True)
        logging.info('Light ON')
    else:
        GPIO.output(light_pin, True)
        controls.setLightStatus(False)
        logging.info('Light OFF')


def switching_fan(boolean, controls):
    if boolean:
        GPIO.output(fan_pin, False)
        controls.setFanStatus(True)
        logging.info('Fan ON')
    else:
        GPIO.output(fan_pin, True)
        controls.setFanStatus(False)
        logging.info('Fan OFF')


# Function for manual controlling with web
def server(status, controls):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 14885))
    sock.listen(1)
    while controls.getWorkingFlag():
        try:
            conn, addr = sock.accept()
            print('connected:', addr)
            logging.info('')
            conn.send('Connected to AGC.')
            while controls.getWorkingFlag():
                status_string = '\nAGC STATUS: \nHumidity = {0}%, \nTemperature = {1} degree, \nLights {2}, \nFan {3},\nAutocontrol {4}'.format(
                    status.getHumidity(),
                    status.getTemperature(),
                    controls.getLightStatus(),
                    controls.getFanStatus(),
                    controls.getAutocontrolFlag())

                conn.send(status_string)
                data = conn.recv(4096)
                if data.decode() == '1':
                    manual_switch('light', controls)
                elif data.decode() == '2':
                    manual_switch('fan', controls)
                    #     elif data.decode() == '3': #remove this, because will send status every second
                    #         conn.send('STATUS update.\n')
                elif data.decode() == '4':
                    controls.setAutocontrolFlag(True)
                    print('Automatical control ON')
                    logging.info('Automatical control ON')
                elif data.decode() == '888':
                    print('Shutdown')
                    controls.setWorkingFlag(False)
                    logging.info('Shutdown')
                else:
                    conn.send('Invalid command.\n')
                    break
            conn.close()
        except socket.error as error:
            print(error)
            logging.error(error)
    sock.close()
    return


# Function for switching mechs by server
def manual_switch(func, controls):
    controls.setAutocontrolFlag(False)
    print('Automatical Control OFF')

    if func == 'light':
        switching_light(not controls.getLightStatus(), controls)

    if func == 'fan':
        switching_fan(not controls.getFanStatus(), controls)


def shutdown():
    GPIO.cleanup()
    sys.exit()


def db_maintenance(status, controls):
    pass
'''
    conn = psycopg2.connect("dbname= user=")
    cur = conn.cursor()
    cur.close()
    conn.close()
'''

# Init threads
agc_thread = threading.Thread(target=agc, args=(status, controls, config))
server_thread = threading.Thread(target=server, args=(status, controls))
db_thread = threading.Thread(target=db_maintenance, args=(status, controls))

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
