# -*- coding: utf-8 -*-
# !/usr/bin/python3

import os
import datetime
import json
import socket
import traceback
import logging
from pigpio_dht import DHT22
from Misc import get911, sendEmail
from sense_hat import SenseHat


def read_dht22_sensor():
    """
    Read temperature and humidity values from the DHT22 sensor.

    Returns:
        temp_c (float): Temperature in Celsius.
        temp_f (float): Temperature in Fahrenheit.
        humidity (float): Relative humidity in percentage.
        is_valid (str): "True" if the reading is valid, "False" if not.

    If an error occurs while reading the sensor, all values are set to "None."
    """

    counter = 0
    while counter < MAX_RETRIES:
        try:
            # Read temperature, humidity, and validity from DHT22 sensor
            DHT_SENSOR = DHT22(SENSOR_DHT22_PIN)
            temp_c, temp_f, humidity, is_valid = DHT_SENSOR.read().values()
            is_valid = "False" if temp_c == 0.0 or temp_f == 0.0 or humidity == 0.0 else str(is_valid)

            # If the reading is valid, return the values
            if is_valid == "True":
                return temp_c, temp_f, humidity, is_valid
        except Exception as ex:
            pass  # Continue to the next retry

        counter += 1

    # If all retries fail, set all values to "None"
    return "None", "None", "None", "None"


def read_senseHat():
    counter = 0
    while counter < MAX_RETRIES:
        try:
            # Read temperature, humidity from Sense Hat
            sense = SenseHat()
            sense.clear()
            temp_c = sense.get_temperature()
            temp_f = temp_c * 9 / 5 + 32
            humidity = sense.get_humidity()

            is_valid = "False" if temp_c == 0.0 or temp_f == 0.0 or humidity == 0.0 else "True"

            # If the reading is valid, return the values
            if is_valid == "True":
                return temp_c, temp_f, humidity, is_valid
        except Exception as ex:
            print(ex)
            pass  # Continue to the next retry

        counter += 1

    # If all retries fail, set all values to "None"
    return "None", "None", "None", "None"


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
    if SENSOR_DHT22_PIN is not False:
        temp_c, temp_f, humidity, valid = read_dht22_sensor()
    elif SENSE_HAT is not False:
        temp_c, temp_f, humidity, valid = read_senseHat()
    else:
        logger.error("No valid config")
        return

    # Failed to measure -> exit
    if valid == "None" or valid == "False":
        logger.error("Failed to measure -> exit")
        return

    # Log currMeasurements
    temp_c, temp_f, humidity = round(temp_c, 2), round(temp_f, 2), round(humidity, 2)
    currMeasurements = {"date": date_now, "temp_c": temp_c, "temp_f": temp_f, "humidity": humidity, "valid": valid}
    logger.info(currMeasurements)

    # Save info to file
    if not os.path.exists(SAVED_INFO_FILE):
        # if the file doesn't exist, create a new empty list
        with open(SAVED_INFO_FILE, "w") as outFile:
            json.dump(list(reversed({})), outFile, indent=2)

    # read the existing data from the file and append the new data to it
    with open(SAVED_INFO_FILE) as inFile:
        data = list(reversed(json.load(inFile)))
        data.append(currMeasurements)

    # write the updated data back to the file
    with open(SAVED_INFO_FILE, "w") as outFile:
        json.dump(list(reversed(data)), outFile, indent=2)

    return


if __name__ == "__main__":
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.abspath(__file__).replace(".py", ".log"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("----------------------------------------------------")

    # Open the configuration file in read mode
    CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(CONFIG_FILE) as inFile:
        CONFIG = json.load(inFile)

    # Sensor Settings
    SAVED_INFO_FILE = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_info.json"))
    hostname = str(socket.gethostname()).upper()
    MAX_RETRIES = CONFIG["MAX_RETRIES"]
    SENSOR_DHT22_PIN = CONFIG[hostname]["SENSOR_DHT22_PIN"]
    SENSE_HAT = CONFIG[hostname]["SENSE_HAT"]

    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
        sendEmail(os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        logger.info("End")
