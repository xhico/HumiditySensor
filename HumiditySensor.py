# -*- coding: utf-8 -*-
# !/usr/bin/python3

# https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/
# python3 -m pip install Adafruit_DHT --no-cache-dir
# nano /home/pi/.local/lib/python3.7/site-packages/Adafruit_DHT/platform_detect.py
# elif match.group(1) == 'BCM2711':
#    return 3

import datetime
import time

import Adafruit_DHT

# Sensor Settings
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

# Humidity && Temperature Lists
humidityList = []
temperatureList = []

# 60 records = 60 mins
maxRecords = 60

# Run forever!
while True:

    # Get humidity, temperature and date now
    date_now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    humidity = round(humidity, 1)
    temperature = round(temperature, 1)
    humidityList.append(humidity)
    temperatureList.append(temperature)

    # Get only the last 60 records
    if len(humidityList) == maxRecords + 1:
        humidityList = humidityList[len(humidityList) - maxRecords:len(humidityList)]
        temperatureList = temperatureList[len(temperatureList) - maxRecords:len(temperatureList)]

    # Calculate Avg for Humidity and Temperature
    humidityAvg = round(sum(humidityList) / len(humidityList), 1)
    temperatureAvg = round(sum(temperatureList) / len(temperatureList), 1)

    # Prints
    print("Date = " + str(date_now))
    print("Humidity = " + str(humidity) + "%")
    print("Temperature = " + str(temperature) + "C")
    print("Humidity Avg = " + str(humidityAvg) + "%")
    print("Temperature Avg = " + str(temperatureAvg) + "C")
    print("")

    # Save info to file
    with open('/home/pi/RaspberryPiHumiditySensor/HumiditySensor.txt', mode='w') as csvFile:
        csvFile.writelines(["date" + ",humidity" + "," + "temperature" + ",humidityAvg" + "," + "temperatureAvg", "\n",
                            str(date_now) + "," + str(humidity) + "," + str(temperature) + "," + str(humidityAvg) + "," + str(temperatureAvg)])
    csvFile.close()

    # Wait 60 secs
    time.sleep(60)
