#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import Adafruit_DHT

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

logging.basicConfig(level = logging.INFO)

class Status():
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
    def setLightStatus(self, a):
        self.light_status = bool(a)

    def setFanStatus(self, a):
        self.fan_status = bool(a)

    def setAutoControl(self, a):
        self.autocontrol = bool(a)

    def setWorking(self, a):
        self.working = bool(a)


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
    except:
        print('Config not found!')
        print('Making config...')
        logging.warning('Config not found!')
        file = open("agc.conf", "w+")
        file.write('[General]' + '\n')
        file.write('max_temperature = 30' + '\n')
        file.write('max_humidity = 50' + '\n')
        file.write('morning_time = 08:00' + '\n')
        file.write('evening_time = 21:00' + '\n')
        file.write('autocontrol = 1' + '\n')
        file.close()
        print('Config complete. Please, restart.')
        sys.exit()


# Making start conditions

status = Status()

controls = Controls()

config = reading_config()

controls.autocontrol = int(config['autocontrol'])


# Function for mechs control
def agc(status, controls, config):
    while controls.working:
        status.setHumidity()
        status.setTemperature()
        status.checkServerTime()
        if controls.autocontrol:
            automaticalControl(status, controls, config)
        time.sleep(0.2)


def automaticalControl(status, controls, config):
    if status.temperature > config['max_temperature'] or status.humidity > config['max_humidity']:
        logging.warning('High temperature or humidity')
        logging.warning(status.temperature)
        logging.warning(status.humidity)
        switching_fan(True, controls)
    elif status.temperature <= (int(config['max_temperature']) - 2):
        switching_fan(False, controls)

    if config['morning_time'] <= status.checkServerTime() <= config['evening_time']:
        switching_light(True, controls)
    else:
        switching_light(False, controls)


def switching_light(boolean, controls):
    if boolean:
        GPIO.output(light_pin, False)
        controls.light_status = True
        logging.info('Light ON')
    else:
        GPIO.output(light_pin, True)
        controls.light_status = False
        logging.info('Light OFF')



def switching_fan(boolean, controls):
    if boolean:
        GPIO.output(fan_pin, False)
        controls.fan_status = True
        logging.info('Fan ON')
    else:
        GPIO.output(fan_pin, True)
        controls.fan_status = False
        logging.info('Fan OFF')



# Function for manual controlling with web
def server(status, controls):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 14885))
    sock.listen(1)
    while controls.working:
        try:
            conn, addr = sock.accept()
            print('connected:', addr)
            logging.info('')
            conn.send('Connected to AGC.')
            while controls.working:
                status_string = '\nAGC STATUS: \nHumidity = {0}%, \nTemperature = {1} degree, \nLights {2}, \nFan {3},\nAutocontrol {4}'.format(
                    status.humidity,
                    status.temperature,
                    controls.light_status,
                    controls.fan_status,
                    controls.autocontrol)

                conn.send(status_string)
                data = conn.recv(4096)
                if data.decode() == '1':
                    manual_switch('light', controls)
                elif data.decode() == '2':
                    manual_switch('fan', controls)
                elif data.decode() == '3':
                    print(status, controls)
                    conn.send('STATUS update.\n')
                elif data.decode() == '4':
                    controls.autocontrol = True
                    print('Automatical control ON')
                    logging.info('Automatical control ON')
                elif data.decode() == '888':
                    print('Shutdown')
                    controls.working = False
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
    controls.autocontrol = False
    print('Automatical Control OFF')

    if func == 'light':
        switching_light(not controls.light_status, controls)

    if func == 'fan':
        switching_fan(not controls.fan_status, controls)


def shutdown():
    GPIO.cleanup()
    sys.exit()


# Init threads
agc_thread = threading.Thread(target=agc, args=(status, controls, config))
server_thread = threading.Thread(target=server, args=(status, controls))

# Start threads

agc_thread.start()
print('Started AGControl')
server_thread.start()
print('Started AGC Server')

# Join threads to the main thread
agc_thread.join()
server_thread.join()

shutdown()
