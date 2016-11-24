import RPi.GPIO as GPIO
import Adafruit_DHT
import logging

###########################
# [Control configuration]#

max_humidity = 50
max_temperature = 30
morning_time = '08:00'  # To turn lights ON
evening_time = '21:00'  # To turn lights OFF
autocontrol = True      # To turn on autocontrol on start

##########################
# [Server configuration]#
server_port = 14880

############################
# [Database configuration]#

db_addr = "host='your database ip address' dbname='default name' user='user' password='password'" # DSN like
time_to_write = r':00:30|:30:30'

########################
# [Mail configuration]#

smtp_server = 'smtp.gmail.com'
smtp_port = 587
agc_mail = 'your_greenery_mail@greenery.com'
agc_mail_pass = 'password'
recieve_mails = ['administrator@greenery.com']

##################################
# [Raspberry GPIO configuration]#

GPIO.setmode(GPIO.BOARD)  # Initialize GPIO
GPIO.setwarnings(False)  # Switch off warnings

light_pin = 7  # Set BOARD rpi.pin for illumination
# pump_pin = 3 # Set BOARD rpi.pin for irrigation
fan_pin = 5  # Set BOARD rpi.pin for ventilation

GPIO.setup(fan_pin, GPIO.OUT)  # Set pin for output
GPIO.setup(light_pin, GPIO.OUT)

GPIO.output(light_pin, True)  # Set output value on start
GPIO.output(fan_pin, True)

sensor = Adafruit_DHT.DHT11  # Sensor initialize
DHT_pin = '14'  # Means BCM.GPIO14 (GPIO.BOARD - 8)

###########################
# [Logging configuration]#

logging.basicConfig(filename='agc_server.log',
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

################################
# [Telegram bot configuration]#

TOKEN = 'your bot token'
administrator_id = 0  # Administrator telegram ID (must be integer).
approved_users = [administrator_id,1,2,3]  # Add more IDs if you need.
