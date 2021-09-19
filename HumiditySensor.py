# https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/
# python3 -m pip install Adafruit_DHT --no-cache-dir
# nano /home/pi/.local/lib/python3.7/site-packages/Adafruit_DHT/platform_detect.py
# elif match.group(1) == 'BCM2711':
#    return 3

import time

import Adafruit_DHT

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        humidity = str(round(humidity, 1))
        temperature = str(round(temperature, 1))
    else:
        humidity = "-1"
        temperature = "-1"

    with open('/home/pi/RaspberryPiHumiditySensor/HumiditySensor.txt', mode='w') as csvFile:
        csvFile.writelines(["humidity" + "," + "temperature", "\n", humidity + "," + temperature])
    csvFile.close()

    # print("Humidity = " + humidity + "%")
    # print("Temperature = " + temperature + "C")
    time.sleep(60)
