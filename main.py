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
import socket # Додаємо імпорт

# Ініціалізація DHT11 один раз за межами циклу
dht_device = adafruit_dht.DHT11(board.D4)  # GPIO 4

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

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
        print('Usage: python3 main.py [DHT11|DHT22|DHT2302] <GPIO pin number> <step, s> [on]')
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
                timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                print(f"{timestamp} Temp(температура)={temperature:0.1f}*C  Humidity(вологість)={humidity:0.1f}%")
                measurementsDb.insert_to_measurements_table(1, str(temperature), timestamp)
                measurementsDb.insert_to_measurements_table(2, str(humidity), timestamp)
                return True
        except RuntimeError:
            pass  # Тиха обробка помилок
        time.sleep(1)  # Затримка між спробами
    return False

# Змінюємо функцію, щоб вона приймала сигнал на зупинку
def run_server(step_s, shutdown_event):
    server.my_server(step_s, shutdown_event)

# Змінюємо функцію, щоб вона приймала сигнал на зупинку
def run_system(sensor, pin, step_s, shutdown_event):
    # Замість while True, перевіряємо, чи не встановлено сигнал
    while not shutdown_event.is_set():
        current_datetime = datetime. datetime.now()
        read_from_dht(current_datetime)
        # Використовуємо join, щоб очікування можна було перервати
        shutdown_event.wait(int(step_s))

if __name__ == "__main__":
    # 1. Зчитуємо параметри запуску з командного рядка
    sensor, pin, step_s, quick_start = read_command_line_params()

    # 2. Викликаємо функцію налаштування бази даних.
    #    Вона поверне True, якщо користувач в меню обрав "1. Run system" або якщо quick_start="on"
    should_run_system = db.create_db(sensor, quick_start)

    # 3. Перевіряємо, чи потрібно запускати основну логіку системи
    if should_run_system:
        # --- ВЕСЬ КОД ДЛЯ ЗАПУСКУ ТЕПЕР ЗНАХОДИТЬСЯ ВСЕРЕДИНІ ЦЬОГО "IF" ---
        
        my_ip = get_local_ip()
        
        try:
            # Оновлюємо IP для першої кімнати (з id=1) в базі даних
            # Переконайтесь, що у файлі db.py є рядок "import roomsDb"
            db.roomsDb.update_ip_in_rooms_table(1, my_ip)
            print("-" * 40)
            print(f"!!! IP-адресу для Кімнати 1 оновлено на {my_ip} в базі даних. !!!")
        except Exception as e:
            print(f"!!! Помилка оновлення IP в базі даних: {e} !!!")

        print("-" * 40)
        print(f"!!! СЕРВЕР ЗАПУСКАЄТЬСЯ НА IP: {my_ip} !!!")
        print(f"!!! Введіть цю IP-адресу у мобільному додатку. !!!")
        print("-" * 40)
        print(f"Запуск системи: датчик={sensor}, пін={pin}, інтервал={step_s} секунд")

        # Створюємо подію для "граціозної" зупинки потоків
        shutdown_event = threading.Event()
        
        t1 = threading.Thread(target=run_server, args=(step_s, shutdown_event))
        t2 = threading.Thread(target=run_system, args=(sensor, pin, step_s, shutdown_event))
        
        t1.start()
        t2.start()

        try:
            # Головний потік чекає тут, доки не буде натиснуто Ctrl+C
            while t1.is_alive() and t2.is_alive():
                t1.join(timeout=1.0) # Чекаємо з таймаутом, щоб не блокуватись назавжди
        except KeyboardInterrupt:
            print("\nОтримано сигнал на зупинку... (Ctrl+C)")
            shutdown_event.set()
        
        # Чекаємо, поки потоки коректно завершаться
        t1.join()
        t2.join()
        print("Роботу системи завершено.")

    else:
        # Цей блок виконається, тільки якщо quick_start="off" і користувач у меню обрав вихід
        print("Налаштування завершено. Запустіть з параметром 'on' або виберіть '1. Run system' в меню.")
