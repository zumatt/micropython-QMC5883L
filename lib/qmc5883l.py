"""
QMC5883L (QST clone of HMC5883) I2C digital compass/magnetometer
driver for micropython.

Changes from original sources:
- Modified reporting format for XYZ data to signed val/scale since the
  data we're interested in is positive/negative gauss.
- Constructor now accepts an I2C object rather than pin definitions, 
  for easier sharing the bus with other devices.
- Tagged most of the useful register bits with names for clarity.
- Added heading calcuation borrowed from a Pi Pico HMC5883 driver.
- Minor cleanups.

Caveats:
- I haven't tested the heading algo for correctness as I'm just using this
as a magnetometer rather than a compass, but I assume if it works with the
Honeywell chip it will also work here.
- Temperature value returned is uncalibrated according to the datasheet,
haven't looked at this aspect much but don't expect anything close to reality
without calibrating your particular chip.


# Usage example with SoftI2C (hard I2C should be identical beyond bus init):
bus = SoftI2C(scl=Pin(3), sda=Pin(4), freq=100000)
qmc = QMC5883L(bus)
(x, y, z, status, temperature) = qmc.read()

Based on: 
 https://github.com/juliantesla13/micropython-esp32-qmc5883/blob/master/QMC5883.py
Which is in turn based on:
 https://github.com/robert-hh/QMC5883/blob/master/qmc5883.py
 https://github.com/gvalkov/micropython-esp8266-hmc5883l/blob/master/hmc5883l.py
Heading algorithm from here:
 https://github.com/peppe8o/rpi-pico-peppe8o/blob/main/libraries/hmc5883l.py
"""

import math
import machine
from ustruct import pack, unpack
from array import array
import time

class QMC5883L():
    REG_CR1 = 0x9
    REG_CR2 = 0xA
    MODE_STBY = 0
    MODE_CONT = 1
    ODR_10HZ = 0
    ODR_50HZ = 1
    ODR_100HZ = 2
    ODR_200HZ = 3
    RNG_2G = 0
    RNG_8G = 1
    OSR_512 = 0
    OSR_256 = 1
    OSR_128 = 2
    OSR_64 = 3
    # scaling factors associated with the two ranges
    RANGESCALE = {RNG_2G:12000, RNG_8G:3000}
    
    def __init__ (self, i2c, address = 13, declination=(7, 42)):
        self.i2c = i2c
        self.address = address
        self.declination = (declination[0] + declination[1] / 60) * math.pi / 180   
        self.scale = 3000
        self.toffset = 0
        # Initialize sensor.
        self.write_config(odr=self.ODR_100HZ, rng=self.RNG_2G, osr=self.OSR_512, mode=self.MODE_CONT)
        # Reserve some memory for the raw xyz measurements.
        self.data = array('B', [0] * 9)        
    
    def reset(self):
        """ Performs a reset of the device by writing to the memory address 0xA (CR2 register), the value of 0b10000000 """
        self.i2c.writeto_mem(self.address, self.REG_CR2, b'\x10000000')

    def stanbdy(self):
        """ Device goes into a sleep state by writing to memory address 0x9 (CR1 register), 0b00 """
        self.i2c.writeto_mem(self.address, self.REG_CR1, b'\x00')
    
    def write_config(self,
                    mode = MODE_CONT,
                    odr = ODR_10HZ,
                    rng = RNG_2G,
                    osr = OSR_512,
                    rol_pnt = 1,
                    int_en = 0):
        """
        Write configuration parameters to device.
        
        Named parameters, default [options], and function:
        mode : MODE_CONT [MODE_STBY] Standby or continuous sampling
        odr : ODR_10HZ [ODR_50HZ | ODR_100HZ | ODR_200HZ] Output data rate
        rng : RNG_2G [RNG_8G] Range
        osr : OSR_512 [OSR_64 | OSR_128 | OSR_256] Oversample ratio
        rol_pnt : Read pointer rollover enable
        int_en : Data available interrupt signal output enable
        """
        if rng in self.RANGESCALE.keys():
            self.scale = self.RANGESCALE[rng]
        else:
            raise Exception("unsupported range value: " + str(rng))
            
        # reset the device before config
        self.reset()
        time.sleep(0.005)
        # bitshift parameters into register values
        cr1_byte = (osr << 6) | (rng << 4) | (odr << 2) | mode
        cr2_byte = (rol_pnt << 6) | int_en
        # print("config cr1 (0x09): ", hex(cr1_byte), " cr2 (0x0A):", hex(cr2_byte))  
        # write out parameters to control registers
        self.i2c.writeto_mem(self.address, self.REG_CR1, bytearray([cr1_byte]))
        self.i2c.writeto_mem(self.address, self.REG_CR2, bytearray([cr2_byte]))
        time.sleep(0.005)
                    
    def read(self):
        """ Performs a read of the data in the position of memory 0x00, by means of a buffer """
        # Read data register 00H ~ 05H.
        self.i2c.readfrom_mem_into(self.address, 0x00, self.data)
        time.sleep(0.005)
        # Unpack data, all values except status come back as signed little endian 16 bit words
        (upx, upy, upz, upstatus, uptemp) = unpack('<hhhbh', self.data)
        # Divide raw values by scale to get result in Gauss
        return (upx / self.scale, upy / self.scale, upz / self.scale,
                upstatus, (uptemp / 100) + self.toffset)
    
    def heading(self, x, y):
        """
        Calculate compass heading based on provided magnetometer X and Y values,
        returns heading (degrees, minutes).
        """
        heading_rad = math.atan2(y, x)
        heading_rad += self.declination

        # Correct reverse heading.
        if heading_rad < 0:
            heading_rad += 2 * math.pi

        # Compensate for wrapping.
        elif heading_rad > 2 * math.pi:
            heading_rad -= 2 * math.pi

        # Convert from radians to degrees.
        heading = heading_rad * 180 / math.pi
        degrees = math.floor(heading)
        minutes = round((heading - degrees) * 60)
        return degrees, minutes

    def format_result(self, x, y, z):
        degrees, minutes = self.heading(x, y)
        return 'X: {:.4f}, Y: {:.4f}, Z: {:.4f}, Heading: {}° {}'.format(x, y, z, degrees, minutes) 