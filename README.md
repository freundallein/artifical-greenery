# artifical-greenery

Client-server app for control artificial greenery.

Artificial Greenery is a little handmade greenhouse, made from 2 IKEA boxes, controled by Raspberry Pi with Raspbian on board.

Server can check temperature and humidity with DHT_11 sensor, switch lights and/or fan, depends on sensor data and daytime;
sending status, recieving commands from simple client, writing log_file.

PostgreSQL is running on virtual machine, write and read through the Internet.

Can send daily reports, also have telegram bot for remote control.


Use Adafruit_DHT lib for reading sensor data from DHT-sensor, psycopg2 for woking with PostgreSQL.


