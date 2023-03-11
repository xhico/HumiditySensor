# -*- coding: utf-8 -*-
# !/usr/bin/python3

# python3 -m pip install yagmail pigpio-dht --no-cache-dir

import os
import datetime
import json
import traceback
import yagmail
import logging
from pigpio_dht import DHT22
from Misc import get911


def getTemp():
    """Get temperature and humidity from DHT22 sensor."""
    try:
        temp_c, temp_f, humidity, valid = DHT_SENSOR.read().values()
        valid = str(valid)
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

    if valid == "None" or valid == "False":
        logger.error("Couldn't get info")
        return

        # Save info to file
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as outFile:
            json.dump(list(reversed({})), outFile, indent=2)
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

    CONFIG_FILE = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "HumiditySensor.json"))

    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
        yagmail.SMTP(EMAIL_USER, EMAIL_APPPW).send(EMAIL_RECEIVER, "Error - " + os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        logger.info("End")
