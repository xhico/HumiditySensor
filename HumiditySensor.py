# -*- coding: utf-8 -*-
# !/usr/bin/python3

# https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/
# python3 -m pip install Adafruit_DHT pyTelegramBotAPI --no-cache-dir
# nano /home/pi/.local/lib/python3.7/site-packages/Adafruit_DHT/platform_detect.py
# elif match.group(1) == 'BCM2711':
#    return 3

import json
import telebot
import datetime
import Adafruit_DHT


def get911(key):
    f = open('/home/pi/.911')
    data = json.load(f)
    f.close()
    return data[key]


TELEGRAM_TOKEN = get911('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = get911('TELEGRAM_CHAT_ID')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

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
    except:
        humidity = "None"
        temperature = "None"

    # Save info to file
    with open('/home/pi/RaspberryPiHumiditySensor/HumiditySensor.txt', mode='w') as csvFile:
        csvFile.writelines(["date" + ",humidity" + "," + "temperature", "\n",
                            str(date_now) + "," + str(humidity) + "," + str(temperature)])
    csvFile.close()

    # # Prints
    # print("Date = " + str(date_now))
    # print("Humidity = " + str(humidity) + "%")
    # print("Temperature = " + str(temperature) + "C")
    # print("")

    # Check if room is on FIRE!!!
    if temperature > 20:
        msg = bot.send_message(TELEGRAM_CHAT_ID,
                               "FIRE!! FIRE!! FIRE!!\n" +
                               "Temperature: " + str(temperature) + "\n" +
                               "Date: " + str(date_now)
                               )
