#!/bin/bash

# Оновлення системи
sudo apt update
sudo apt upgrade -y

# Встановлення pip, якщо ще не встановлений
sudo apt install python3-pip -y

# Встановлення необхідних бібліотек
pip3 install pymysql
pip3 install Adafruit_DHT
pip3 install RPi.GPIO
pip3 install smbus2
