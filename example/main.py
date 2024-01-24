import qmc5883l
from machine import I2C
from time import sleep_ms

bus = I2C(0)
qmc = qmc5883l.QMC5883L(bus)

while True:
  (x, y, z, status, temperature) = qmc.read()
  deg = qmc.heading(x,y)[0]
  
  print(deg)
  sleep_ms(200)