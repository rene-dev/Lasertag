import os
import time
import smbus
bus = smbus.SMBus(1)
address = 0x18

while True:

        if bus.read_byte_data(address, 0) == 0:
                os.system("aplay pew1.wav")
