#!/bin/bash

sudo mv /home/pi/HumiditySensor/HumiditySensor.service /etc/systemd/system/ && sudo systemctl daemon-reload
python3 -m pip install yagmail pigpio-dht --no-cache-dir
sudo apt install pigpiod -y
sudo pigpiod
chmod +x -R /home/pi/HumiditySensor/*