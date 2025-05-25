# DiplomaProject_ServerPart
Software component run on Raspberry Pi server

In the process of development Raspberry Pi, Python, Visual Studio Code and console interface were used.

In order to run this application you have to connect DHT11 sensor to Raspberry Pi. 
After that, make sure that your network address is static. And, run system by command (as example):

'python3 main.py <DHT sensor> <GPIO> <time> <quickstart>' ('python3 main.py 11 4 on 15 off).

- DHT sensor may be: DHT11, DHT22 or DHT2302;
- GPIO is pin on RPi, connected to DHT sensor;
- time is decimal integer which equals to delay between two consistent measurements;
- quickstart option allows us (when on) to simply run the server without entering main menu.

In main menu user can add, edit, delete and see all the components. You just need to type appropriate number to choose your operation.

NOTE: client application shows only last saved measurements if it`s not connected to server.
