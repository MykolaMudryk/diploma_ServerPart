#!/usr/bin/python
# Python scripts for running Microclimate System.
import sys
import threading
import adafruit_dht
import board
import datetime
import time
import server
import db
import measurementsDb

# Ініціалізація DHT11 один раз за межами циклу
dht_device = adafruit_dht.DHT11(board.D4)  # GPIO 4

# parse command line parameters
def read_command_line_params():
    step_s = 10  # default time between two measurements, s
    quick_start = "off"
    sensor_args = {'DHT11': None, 'DHT22': None, 'DHT2302': None}
    if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
        sensor = sys.argv[1]
        pin = sys.argv[2]
    elif len(sys.argv) == 4 and sys.argv[1] in sensor_args:
        sensor = sys.argv[1]
        pin = sys.argv[2]
        step_s = sys.argv[3]
    elif len(sys.argv) == 5 and sys.argv[1] in sensor_args:
        sensor = sys.argv[1]
        pin = sys.argv[2]
        step_s = sys.argv[3]
        quick_start = sys.argv[4]  # "on" як 5-й аргумент
    else:
        print('ENGLISH description:')
        print('Usage: python3 main.py [DHT11|DHT22|DHT2302] <GPIO pin number> <step, s> [on]')
        print('Example 1: python3 main.py DHT11 4 - '
              'Read from an DHT11 connected to GPIO pin #4')
        print('Example 2: python3 main.py DHT11 4 10 on - '
              'Quick start with 10s interval from DHT11 on GPIO pin #4')
        print('---------------------------')
        print('УКРАЇНСЬКОЮ пояснення:')
        print('Застосування: python3 main.py [DHT11|DHT22|DHT2302] <GPIO номер виводу> <період, с> [on]')
        print('Приклад 1: python3 main.py DHT11 4 - '
              'Прочитати дані з DHT11, підключеного до GPIO-виводу #4')
        print('Приклад 2: python3 main.py DHT11 4 10 on - '
              'Швидкий запуск із зчитуванням кожні 10 секунд з DHT11 на GPIO #4')
        sys.exit(1)
    return sensor, pin, step_s, quick_start

# read current temperature and humidity silently
def read_from_dht(current_datetime):
    global dht_device
    max_retries = 5
    for _ in range(max_retries):
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            if humidity is not None and temperature is not None:
                timestamp = current_datetime.strftime("%d-%m-%Y %H:%M:%S")
                print(f"{timestamp} Temp(температура)={temperature:0.1f}*C  Humidity(вологість)={humidity:0.1f}%")
                measurementsDb.insert_to_measurements_table(1, str(temperature), timestamp)
                measurementsDb.insert_to_measurements_table(2, str(humidity), timestamp)
                return True
        except RuntimeError:
            pass  # Тиха обробка помилок
        time.sleep(1)  # Затримка між спробами
    # Якщо всі спроби невдалі, просто пропускаємо вивід
    return False

def run_server(step_s):
    server.my_server(step_s)  # Передаємо step_s у my_server

def run_system(sensor, pin, step_s):
    while True:
        current_datetime = datetime.datetime.now()
        read_from_dht(current_datetime)
        time.sleep(int(step_s))

if __name__ == "__main__":
    sensor, pin, step_s, quick_start = read_command_line_params()
    should_run_system = db.create_db(sensor, quick_start)

    if quick_start == "on" or should_run_system:
        print(f"Starting system with sensor {sensor} on pin {pin}, step {step_s} seconds")
        t1 = threading.Thread(target=run_server, args=(step_s,))
        t2 = threading.Thread(target=run_system, args=(sensor, pin, step_s))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    else:
        print("System configuration completed. Run with 'on' or select 'Run system' to start.")