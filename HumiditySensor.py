# -*- coding: utf-8 -*-
# !/usr/bin/python3

# https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/
# python3 -m pip install Adafruit_DHT yagmail --no-cache-dir
# nano /home/pi/.local/lib/python3.7/site-packages/Adafruit_DHT/platform_detect.py
# elif match.group(1) == 'BCM2711':
#    return 3

import datetime
import json

import Adafruit_DHT
import yagmail


def get911(key):
    with open('/home/pi/.911') as f:
        data = json.load(f)
    return data[key]


EMAIL_USER = get911('EMAIL_USER')
EMAIL_APPPW = get911('EMAIL_APPPW')
EMAIL_RECEIVER = get911('EMAIL_RECEIVER')

# Sensor Settings
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

if __name__ == "__main__":
    # Get humidity, temperature and date now
    date_now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    try:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        humidity = round(humidity, 1)
        temperature = round(temperature, 1)
        print("Humidity: " + str(humidity))
        print("Temperature: " + str(temperature))
        
        # Check if room is on FIRE!!!
        if temperature > 20:
            yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "FIRE!! FIRE!! FIRE!!",
                                                       "Temperature: " + str(temperature) + "°C" "\n" +
                                                       "Humidity: " + str(humidity) + "%" + "\n" +
                                                       "Date: " + str(date_now)
                                                       )
    except Exception as ex:
        print(ex)
        humidity = "None"
        temperature = "None"

    # Save info to file
    with open('/home/pi/HumiditySensor/HumiditySensor.txt', mode='w') as csvFile:
        csvFile.writelines(["date" + ",humidity" + "," + "temperature", "\n",
                            str(date_now) + "," + str(humidity) + "," + str(temperature)])
    csvFile.close()


