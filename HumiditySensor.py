# -*- coding: utf-8 -*-
# !/usr/bin/python3

import datetime
import json
import yagmail
from pigpio_dht import DHT22
import os


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


def sendMain(temp_c, temp_f, humidity, date_now):
    bodyContent = "temp_c: " + temp_c + "°C" + "\n" + "temp_f: " + temp_f + "°F" + "\n" + "Humidity: " + humidity + "%" + "\n" + "Date: " + date_now
    yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "FIRE!! FIRE!! FIRE!!", bodyContent)


def getTemp():
    try:
        temp_c, temp_f, humidity, valid = DHT_SENSOR.read().values()
        temp_c, temp_f, humidity, valid = str(temp_c), str(temp_f), str(humidity), str(valid)
    except Exception:
        temp_c, temp_f, humidity, valid = "None", "None", "None", "None"

    return temp_c, temp_f, humidity, valid


def main():
    print("----------------------------------------------------")
    print(str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")))

    # Get humidity, temperature and date now
    date_now = str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M"))

    # Get Sensor Info
    temp_c, temp_f, humidity, valid = getTemp()

    # Retry if failed
    counter = 1
    while (valid == "None" or valid == "False") and counter < 5:
        print(counter, "Retry")
        temp_c, temp_f, humidity, valid = getTemp()
        counter += 1

    print("temp_c: " + temp_c + "\n" + "temp_f: " + temp_f + "\n" + "Humidity: " + humidity + "\n" + "Valid: " + valid)

    # Check if room is on FIRE!!!
    if int(float(temp_c)) > 30 and temp_c != "None":
        print("Fire")
        sendMain(temp_c, temp_f, humidity, date_now)

    # Save info to file
    LOG_FILE = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "HumiditySensor.json"))
    with open(LOG_FILE) as inFile:
        data = list(reversed(json.load(inFile)))
        data.append({"date": date_now, "temp_c": temp_c, "temp_f": temp_f, "humidity": humidity, "valid": valid})
    with open(LOG_FILE, "w") as outFile:
        json.dump(list(reversed(data)), outFile, indent=2)


if __name__ == "__main__":
    main()
