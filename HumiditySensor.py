# -*- coding: utf-8 -*-
# !/usr/bin/python3

import os
import datetime
import json
import socket
import traceback
import logging
from pigpio_dht import DHT22
from sense_hat import SenseHat
from Misc import get911, sendEmail


def read_sensor(sensor):
    """
    Read sensor data.

    Args:
        sensor (str): The type of sensor to read ("SenseHat" or "DHT22").

    Returns:
        dict: A dictionary containing sensor measurements.
    """
    counter = 0
    info = {"date": str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M")), "temp_c": 0, "temp_f": 0, "humidity": 0}

    while any(val == 0 for val in info.values()):
        if sensor == "SenseHat":
            sense = SenseHat()
            info["temp_c"] = round(sense.get_temperature(), 2)
            info["temp_f"] = round(info["temp_c"] * 9 / 5 + 32, 2)
            info["humidity"] = round(sense.get_humidity(), 2)
            info["pressure"] = round(sense.get_pressure(), 2)

        if sensor == "DHT22":
            dht22 = DHT22(SENSOR_DHT22_PIN).read(retries=MAX_RETRIES)
            info["temp_c"] = round(dht22["temp_c"], 2)
            info["temp_f"] = round(dht22["temp_f"], 2)
            info["humidity"] = round(dht22["humidity"], 2)

        if counter == 5:
            return None

        counter += 1

    return info


def main():
    """
    Main function to collect sensor data and save it to a file.
    """

    # Set Sensor
    if SENSE_HAT:
        sensor = "SenseHat"
    elif SENSOR_DHT22_PIN:
        sensor = "DHT22"
    else:
        logger.error("Failed to set Sensor, check config")
        return

    # Get Measurements
    logger.info("Sensor: " + sensor)
    measurements = read_sensor(sensor)

    # Check for valid measurements
    if measurements is None:
        logger.error("Failed to get measurements")
        return

    # Log measurements
    for key, val in measurements.items():
        logger.info(key + " - " + str(val))

    # Create SAVED_INFO_FILE if it doesn't exist
    if not os.path.exists(SAVED_INFO_FILE):
        with open(SAVED_INFO_FILE, "w") as outFile:
            json.dump(list(reversed({})), outFile, indent=2)

    # Read the existing data from the file and append the new data to it
    with open(SAVED_INFO_FILE) as inFile:
        data = list(reversed(json.load(inFile)))
        data.append(measurements)

    # Save data
    with open(SAVED_INFO_FILE, "w") as outFile:
        json.dump(list(reversed(data)), outFile, indent=2)


if __name__ == "__main__":
    # Set Logging
    LOG_FILE = f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{os.path.abspath(__file__).replace(".py", ".log")}")}"
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("----------------------------------------------------")

    # Open the configuration file in read mode
    CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(CONFIG_FILE) as inFile:
        CONFIG = json.load(inFile)

    # Sensor Settings
    hostname = str(socket.gethostname()).upper()
    SAVED_INFO_FILE = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_info.json"))
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
