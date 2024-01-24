# Introduction

Fork of https://github.com/kmm/micropython-QMC5883L

This is a library for the QMC5883L, a 3-Axis Compass Magnetometer module.

![QMC5883L Board](https://www.bastelgarage.ch/image/cache/catalog/Artikel/420041-420050/420042-9113-1000x1000.jpg)

The module can be controlled via I2C port.

## Installation
Just copy the file lib/qmc5883l.py to your MicroPython board's root or inside its lib directory if Block Device is supported

## Usage
Import the library, setup the I2C and the qmc5883l module.

You find an example of usage in the file main.py

## References
* Based on: 
	* https://github.com/kmm/micropython-QMC5883L
* Which is in turn based on:
 	* https://github.com/juliantesla13/micropython-esp32-qmc5883/blob/master/QMC5883.py
	* https://github.com/robert-hh/QMC5883/blob/master/qmc5883.py
	* https://github.com/gvalkov/micropython-esp8266-hmc5883l/blob/master/hmc5883l.py
* Heading algorithm from here:
	* https://github.com/peppe8o/rpi-pico-peppe8o/blob/main/libraries/hmc5883l.py
