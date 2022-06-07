# -*- coding: utf-8 -*-
# !/usr/bin/python3

import datetime
import json
import yagmail
from pigpio_dht import DHT22



def get911(key):
    with open('/home/pi/.911') as f:
        data = json.load(f)
    return data[key]


# Email Settings
EMAIL_USER = get911('EMAIL_USER')
EMAIL_APPPW = get911('EMAIL_APPPW')
EMAIL_RECEIVER = get911('EMAIL_RECEIVER')

# Sensor Settings
DHT_PIN = 4
DHT_SENSOR = DHT22(DHT_PIN)


if __name__ == "__main__":
    # Get humidity, temperature and date now
    date_now = str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

    # Get Sensor Info
    try:
        temp_c, temp_f, humidity, valid = DHT_SENSOR.read().values()
        temp_c, temp_f, humidity, valid = str(temp_c), str(temp_f), str(humidity), str(valid)

        # Check if room is on FIRE!!!
        if int(float(temp_c)) > 30:
            bodyContent = "temp_c: " + temp_c + "°C" + "\n" + "temp_f: " + temp_f + "°F" + "\n" + "Humidity: " + humidity + "%" + "\n" + "Date: " + date_now + "\n" + "Valid: " + valid
            yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "FIRE!! FIRE!! FIRE!!", bodyContent)

    except Exception:
        temp_c, temp_f, humidity, valid = "None", "None", "None", "None"


    # Save info to file
    print("temp_c: " + temp_c)
    print("temp_f: " + temp_f)
    print("Humidity: " + humidity)
    print("Valid: " + valid)
    with open('/home/pi/HumiditySensor/HumiditySensor.txt', mode='w') as csvFile:
        csvFile.writelines(["date, temp_c, temp_f, humidity, valid\n", date_now + ", " + temp_c + ", " + temp_f, ", " + humidity + ", " + valid])


