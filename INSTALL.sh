#!/bin/bash

sudo mv /home/pi/HumiditySensor/HumiditySensor.service /etc/systemd/system/ && sudo systemctl daemon-reload
python3 -m pip install -r /home/pi/HumiditySensor/requirements.txt --no-cache-dir
sudo apt install pigpiod sense-hat -y
sudo pigpiod
chmod +x -R /home/pi/HumiditySensor/*
sudo mkdir -p /home/pi/.config/sense_hat
sudo chown -R pi:pi /home/pi/.config/sense_hat
