# -*- coding: utf-8 -*-
# !/usr/bin/python3

# python3 -m pip install yagmail pigpio-dht --no-cache-dir

import os
import datetime
import json
import traceback
import base64
import yagmail
import logging
from pigpio_dht import DHT22
from Misc import get911


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
    # Get humidity, temperature and date now
    date_now = str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M"))

    # Get Sensor Info
    temp_c, temp_f, humidity, valid = getTemp()

    # Retry if failed
    counter = 1
    while (valid == "None" or valid == "False") and counter < 5:
        logger.info(counter, "Retry")
        temp_c, temp_f, humidity, valid = getTemp()
        counter += 1

    logger.info("temp_c: " + temp_c)
    logger.info("temp_f: " + temp_f)
    logger.info("Humidity: " + humidity)
    logger.info("Valid: " + valid)

    # Check if room is on FIRE!!!
    if int(float(temp_c)) > 30 and temp_c != "None":
        logger.info("Fire")
        sendMain(temp_c, temp_f, humidity, date_now)

    # Save info to file
    CONFIG_FILE = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "HumiditySensor.json"))
    with open(CONFIG_FILE) as inFile:
        data = list(reversed(json.load(inFile)))
        data.append({"date": date_now, "temp_c": temp_c, "temp_f": temp_f, "humidity": humidity, "valid": valid})
    with open(CONFIG_FILE, "w") as outFile:
        json.dump(list(reversed(data)), outFile, indent=2)


if __name__ == "__main__":
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.abspath(__file__).replace(".py", ".log"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("----------------------------------------------------")

    # Email Settings
    EMAIL_USER = get911('EMAIL_USER')
    EMAIL_APPPW = get911('EMAIL_APPPW')
    EMAIL_RECEIVER = get911('EMAIL_RECEIVER')

    # Sensor Settings
    DHT_PIN = 4
    DHT_SENSOR = DHT22(DHT_PIN)

    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
        yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "Error - " + os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        logger.info("End")
