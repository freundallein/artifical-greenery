#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import Adafruit_DHT

import sys
import time
import threading
import socket

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
        file = open("agc.conf", "w+")
        file.write('[General]' + '\n')
        file.write('max_temperature = 30' + '\n')
        file.write('max_humidity = 50' + '\n')
        file.write('morning_time = 09:00' + '\n')
        file.write('evening_time = 22:00' + '\n')
        file.write('autocontrol = 1' + '\n')
        file.close()
        print('Config complete. Please, restart.')
        sys.exit()


# Making start conditions


status = {'humidity': 0,
          'temperature': 0}

controls = {'light_status': False,
            'fan_status': False,
            'autocontrol': True,
            'working': True}

config = reading_config()

controls['autocontrol'] = int(config['autocontrol'])


# Function for mechs control
def agc(status, controls, config):
    while controls['working']:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, DHT_pin)
        status['humidity'] = humidity
        status['temperature'] = temperature
        if controls['autocontrol']:
            autocontrol(status, controls, config)
        time.sleep(0.2)

def autocontrol(status, controls, config):
    if status['temperature'] > config['max_temperature'] or status['humidity'] > config['max_humidity']:
        switching_fan(True, controls)
    elif status['temperature'] <= (int(config['max_temperature']) - 2):
        switching_fan(False, controls)


    if config['morning_time'] <= time.strftime('%H:%M') <= config['evening_time']:
        switching_light(True, controls)
    else:
        switching_light(False, controls)


def switching_light(boolean, controls):
    if not boolean:
        GPIO.output(light_pin, True)
        controls['light_status'] = False
    else:
        GPIO.output(light_pin, False)
        controls['light_status'] = True


def switching_fan(boolean, controls):
    if not boolean:
        GPIO.output(fan_pin, True)
        controls['fan_status'] = False
    else:
        GPIO.output(fan_pin, False)
        controls['fan_status'] = True


# Function for manual controlling with web
def server(status, controls):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 14885))
    sock.listen(1)
    while controls['working']:
        try:
            conn, addr = sock.accept()
            print('connected:', addr)
            conn.send('Connected to AGC.')
            while controls['working']:
                status_string = '\nAGC STATUS: \nHumidity = {0}%, \nTemperature = {1} degree, \nLights {2}, \nFan {3}'.format(
                    status['humidity'],
                    status['temperature'],
                    controls['light_status'],
                    controls['fan_status'])

                conn.send(status_string)
                data = conn.recv(4096)
                if data.decode() == '1':
                    manual_switch('light', controls)
                elif data.decode() == '2':
                    manual_switch('fan', controls)
                elif data.decode() == '3':
                    print(status,controls)
                    conn.send('STATUS update.\n')
                elif data.decode() == '4':
                    controls['autocontrol'] = True
                    print('Automatical control ON')
                elif data.decode() == '888':
                    print('Shutdown')
                    controls['working'] = False
                else:
                    conn.send('Invalid command.\n')
                    break
            conn.close()
        except socket.error as error:
            print(error)
    sock.close()
    return



# Function for switching mechs by server
def manual_switch(func, controls):
    controls['autocontrol'] = False
    print('Automatical Control OFF')

    if func == 'light' and controls['light_status']:
        switching_light(False, controls)
    elif func == 'light' and not controls['light_status']:
        switching_light(True, controls)

    if func == 'fan' and controls['fan_status']:
        switching_fan(False, controls)
    elif func == 'fan' and not controls['fan_status']:
        switching_fan(True, controls)


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
