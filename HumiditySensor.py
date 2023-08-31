# -*- coding: utf-8 -*-
# !/usr/bin/python3

import os
import datetime
import json
import traceback
import logging
from pigpio_dht import DHT22
from Misc import get911, sendErrorEmail


def getTemp():
    """
    Reads the temperature and humidity from the DHT22 sensor.

    Returns:
    temp_c (float): temperature in Celsius
    temp_f (float): temperature in Fahrenheit
    humidity (float): relative humidity in percentage
    valid (str): "True" if the reading is valid, "False" if not

    If an error occurs while reading the sensor, all values are set to "None".
    """
    try:
        # read temperature, humidity, and validity from DHT22 sensor
        temp_c, temp_f, humidity, valid = DHT_SENSOR.read().values()
        valid = str(valid)  # convert boolean value to string "True" or "False"
    except Exception:
        # if an error occurs, set all values to "None"
        temp_c, temp_f, humidity, valid = "None", "None", "None", "None"
    return temp_c, temp_f, humidity, valid  # return a tuple of four values


def main():
    """
    Main function that reads temperature and humidity data from a sensor and saves it to a file.

    If the sensor reading fails, it will retry up to 5 times before giving up.
    The data is saved to a JSON file with the following format:
    [
        {
            "date": "2023/03/11 10:30",
            "temp_c": 20.0,
            "temp_f": 68.0,
            "humidity": 50.0,
            "valid": "True"
        },
        ...
    ]
    """
    # Get humidity, temperature and date now
    date_now = str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M"))

    # Get Sensor Info
    logger.info("Get Sensor Info")
    temp_c, temp_f, humidity, valid = getTemp()

    # Retry if failed
    counter = 1
    while (valid == "None" or valid == "False") and counter < 5:
        logger.info(counter, "Retry")
        temp_c, temp_f, humidity, valid = getTemp()
        counter += 1

    # Failed to measure -> exit
    if valid == "None" or valid == "False":
        logger.error("Failed to measure -> exit")
        return

    # Log currMeasurements
    currMeasurements = {"date": date_now, "temp_c": temp_c, "temp_f": temp_f, "humidity": humidity, "valid": valid}
    logger.info(currMeasurements)

    # Save info to file
    if not os.path.exists(CONFIG_FILE):
        # if the file doesn't exist, create a new empty list
        with open(CONFIG_FILE, "w") as outFile:
            json.dump(list(reversed({})), outFile, indent=2)
    with open(CONFIG_FILE) as inFile:
        # read the existing data from the file and append the new data to it
        data = list(reversed(json.load(inFile)))
        data.append(currMeasurements)
    with open(CONFIG_FILE, "w") as outFile:
        # write the updated data back to the file
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
    CONFIG_FILE = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"))
    DHT_PIN = 4
    DHT_SENSOR = DHT22(DHT_PIN)

    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
        sendErrorEmail(os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        logger.info("End")
