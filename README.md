# artifical-greenery

Client-server app for control artificial greenery.

Artificial Greenery is a little handmade greenhouse, made from 2 IKEA boxes, controled by Raspberry Pi with Raspbian on board.

Server can check temperature and humidity with DHT_11 sensor, switch lights and/or fan, depends on sensor data and daytime;
sending status, recieving commands from client, writing log_file.

DB based on PostgreSQL upcoming.

Use Adafruit_DHT lib for reading sensor data from DHT-sensor.


