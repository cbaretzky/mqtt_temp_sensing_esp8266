# Mosquitto temperature logger for an esp8266 running µpython

This repository contains an example for a boot.py and main.py to work with an esp8266 running [micropython](https://github.com/micropython/micropython)

The code will do the following steps:
  1. Wake the esp8266 periodically (and shut it down if something goes wrong)
  2. Connect to a given wifi network (Goes to sleep if the wifi connection fails)
  3. Read the values from several ds18b20 temperature sensors
  4. Read the humidity and temperature from a dht11 sensors
  5. Write the values to flash
  6. Send the values to a remote Mosquitto broker.
  7. Put the esp8266 back into deepsleep

The code is specifically written for a [wio node](http://wiki.seeedstudio.com/Wio_Node/) style device which can power down external sensors via gpio.
