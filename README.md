# micropython-QMC5883L

> Micropython driver for QMC5883L digital compass

## Overview

Should be compatible with most micropython platforms, tested on ESP32-C3.

## Example Usage
```python
import qmc5883l
bus = SoftI2C(scl=Pin(3), sda=Pin(4), freq=100000)
qmc = QMC5883L(bus)
(x, y, z, status, temperature) = qmc.read()
```

## References
* Based on: 
	* https://github.com/juliantesla13/micropython-esp32-qmc5883/blob/master/QMC5883.py
* Which is in turn based on:
	* https://github.com/robert-hh/QMC5883/blob/master/qmc5883.py
	* https://github.com/gvalkov/micropython-esp8266-hmc5883l/blob/master/hmc5883l.py
* Heading algorithm from here:
	* https://github.com/peppe8o/rpi-pico-peppe8o/blob/main/libraries/hmc5883l.py