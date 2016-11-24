import logging
import time

import Adafruit_DHT
import RPi.GPIO as GPIO

from package import config


class Status:
    def __init__(self):
        self.humidity, self.temperature = Adafruit_DHT.read_retry(config.sensor, config.DHT_pin)

    def set_humidity(self):
        self.humidity = Adafruit_DHT.read_retry(config.sensor, config.DHT_pin)[0]

    def set_temperature(self):
        self.temperature = Adafruit_DHT.read_retry(config.sensor, config.DHT_pin)[1]

    def get_humidity(self):
        return self.humidity

    def get_temperature(self):
        return self.temperature

    def check_server_time(self):
        return time.strftime('%H:%M')


class Controls:
    def __init__(self):
        self.light_status = False
        self.fan_status = False
        self.working_flag = True
        self.autocontrol_flag = config.autocontrol
        self.morning_time = config.morning_time
        self.evening_time = config.evening_time
        self.max_temperature = config.max_temperature
        self.max_humidity = config.max_humidity

    def set_light_status(self, flag):
        flag=bool(flag)
        if flag != self.light_status:
            if flag:
                logging.info('Lights ON')
            else:
                logging.info('Lights OFF')
        self.light_status = bool(flag)

    def set_fan_status(self, flag):
        flag = bool(flag)
        if flag != self.fan_status:
            if flag:
                logging.info('Fan ON')
            else:
                logging.info('Fan OFF')
        self.fan_status = bool(flag)

    def set_autocontrol_flag(self, flag):
        self.autocontrol_flag = bool(flag)

    def set_working_flag(self, flag):
        self.working_flag = bool(flag)

    def get_light_status(self):
        return self.light_status

    def get_fan_status(self):
        return self.fan_status

    def get_autocontrol_flag(self):
        return self.autocontrol_flag

    def get_working_flag(self):
        return self.working_flag

    def get_morning_time(self):
        return self.morning_time

    def get_evening_time(self):
        return self.evening_time

    def get_max_temperature(self):
        return self.max_temperature

    def get_max_humidity(self):
        return self.max_humidity


# Main function for mechanism control
def agc():
    while controls.get_working_flag():
        status.set_humidity()
        status.set_temperature()
        if controls.get_autocontrol_flag():
            automatic_control()
        time.sleep(0.5)


def automatic_control():
    if status.get_temperature() > controls.get_max_temperature():
        logging.warning('High temperature: %i', status.get_temperature())
        switching_fan(True)

    elif status.get_humidity() > controls.get_max_humidity():
        logging.warning('High humidity: %i', status.get_humidity())
        switching_fan(True)

    elif status.get_temperature() <= (controls.get_max_temperature() - 5) and status.get_humidity() <= (
                controls.get_max_humidity() - 5):
        switching_fan(False)

    if controls.get_morning_time() <= status.check_server_time() <= controls.get_evening_time():
        switching_light(True)
    else:
        switching_light(False)


def switching_light(boolean):
    GPIO.output(config.light_pin, not boolean)
    controls.set_light_status(boolean)


def switching_fan(boolean):
    GPIO.output(config.fan_pin, not boolean)
    controls.set_fan_status(boolean)


# Function for switching mechanism by server
def manual_switch(func):
    controls.set_autocontrol_flag(False)
    logging.info('Automatic Control OFF')
    if func == 'light':
        switching_light(not controls.get_light_status())

    if func == 'fan':
        switching_fan(not controls.get_fan_status())


def get_status():
    status_msg = '***Artificial Greenery*** \nHumidity = ' + str(status.get_humidity()) + '\n' + 'Temperature = ' + str(
        status.get_temperature()) + '\n' + 'Lights = ' + str(
        controls.get_light_status()) + '\n' + 'Fan = ' + str(controls.get_fan_status()) + '\n' + 'Autocontrol = ' + str(
        controls.get_autocontrol_flag())
    return status_msg


status = Status()
controls = Controls()
