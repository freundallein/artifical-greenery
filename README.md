# artificial-greenery

Artificial Greenery is a little handmade greenhouse, made from 2 IKEA boxes, controled by Raspberry Pi with Raspbian on board.

Artificial Greenery can:
- check temperature and humidity with DHT_11 sensor
- switch lights and/or fan, depends on sensor data and daytime
- send status
- mail daily report 
- recieve commands from simple client
- write log_file
- save data to SQL Satabase
- be controled by mobile phone using Telegram.
PostgreSQL is running on virtual machine, write and read through the Internet.

For proper work you will nedd to install libraries:
```
Adafruit_DHT
RPi.GPIO
psycopg2
telebot
```

Run main.py for start (should be root for GPIO).

For any questions contact:
- freund.allein@gmail.com


