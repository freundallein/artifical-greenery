import logging
import time
import RPi.GPIO as GPIO
import Adafruit_DHT
import sys

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


def reading_config():
    try:
        config_file = open('agc.conf', 'r')
        config_line = config_file.read().split('\n')
        config = {}
        for i in range(len(config_line)):
            if ((('[' and']') or '#') in config_line[i]) or (not config_line[i]):
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
        file.write('[Database Mailing configuration]' + '\n')
        file.write('smtp_server =  smtp.gmail.com' + '\n')
        file.write('smtp_port =  587' + '\n')
        file.write('agc_mail = ' + '\n')
        file.write('agc_mail_pass =  ' + '\n')
        file.write('recieve_mail =  ' + '\n')
        file.close()
        print('Config complete. Please, restart.')
        logging.info('Config complete')
        sys.exit()


class Status:
    def __init__(self):
        self.humidity, self.temperature = Adafruit_DHT.read_retry(sensor, DHT_pin)

    def set_humidity(self):
        self.humidity = Adafruit_DHT.read_retry(sensor, DHT_pin)[0]

    def set_temperature(self):
        self.temperature = Adafruit_DHT.read_retry(sensor, DHT_pin)[1]

    def get_humidity(self):
        return self.humidity

    def get_temperature(self):
        return self.temperature

    def check_server_time(self):
        return time.strftime('%H:%M')


class Controls:
    def __init__(self, config):
        self.light_status = False
        self.fan_status = False
        self.working_flag = True
        self.autocontrol_flag = bool(config['autocontrol'])
        self.morning_time = config['morning_time']
        self.evening_time = config['evening_time']
        self.max_temperature = int(config['max_temperature'])
        self.max_humidity = int(config['max_humidity'])

    def set_light_status(self, flag):
        self.light_status = bool(flag)

    def set_fan_status(self, flag):
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


# Making start conditions
CONFIG = reading_config()

status = Status()
controls = Controls(CONFIG)


# Function for mechs control
def agc():
    while controls.get_working_flag():
        status.set_humidity()
        status.set_temperature()
        if controls.get_autocontrol_flag():
            automatical_control()
        time.sleep(0.5)


def automatical_control():
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
    if boolean:
        GPIO.output(light_pin, False)
        controls.set_light_status(True)
        logging.info('Lights ON')
    else:
        GPIO.output(light_pin, True)
        controls.set_light_status(False)
        logging.info('Lights OFF')


def switching_fan(boolean):
    if boolean:
        GPIO.output(fan_pin, False)
        controls.set_fan_status(True)
        logging.info('Fan ON')
    else:
        GPIO.output(fan_pin, True)
        controls.set_fan_status(False)
        logging.info('Fan OFF')


# Function for switching mechs by server
def manual_switch(func):
    controls.set_autocontrol_flag(False)
    print('Automatical Control OFF')

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
