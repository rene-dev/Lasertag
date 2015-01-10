#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import logging
import smbus 

"""	addr 0x18
	  0	  1	  2	  3	  4	  5	  6	  7		8		9		10	 11		12	  13	 14  15  16
0x10  LED_R  LED_G  LED_B  LED_W																						  Live
0x18  Fire   Key	Key	LED_R  LED_G  LED_B  LED_W  Laser_R  Laser_G  Laser_B  TxPID  TxDamage  Haptic  alive
"""

logger = logging.getLogger(__name__)

class Hardware:
	adrTrefferModule = 0x10
	adrLaserModule = 0x18

	def __init__(self):
		self.bus = smbus.SMBus(0)
		self.getFire()
		self.getLive()
		self.setLaser(R=0, G=0, B=0)
		self.setFrontLED(R=0, G=0, B=0, W=0)
		self.setTopLED(R=0, G=0, B=0, W=0)

	def getLaserModule(self, register):
		return self.bus.read_byte_data(self.adrLaserModule, register)

	def setLaserModule(self, register, data):
		self.bus.write_byte_data(self.adrLaserModule, register, data)

	def getTrefferModule(self, register):
		return self.bus.read_byte_data(self.adrTrefferModule, register)

	def setTrefferModule(self, register, data):
		self.bus.write_byte_data(self.adrTrefferModule, register, data)

	def getFire(self):
		return self.getLaserModule(0x00)

	def getLive(self):
		return self.getTrefferModule(0x10)

	def setLaser(self, R=None, G=None, B=None):
		if R is not None:
			self.setLaserModule(7, R)
		if G is not None:
			self.setLaserModule(8, G)
		if B is not None:
			self.setLaserModule(9, B)

	def setTopLED(self, R=None, G=None, B=None, W=None):
		if R is not None:
			self.setTrefferModule(0, R)
		if G is not None:
			self.setTrefferModule(1, G)
		if B is not None:
			self.setTrefferModule(2, B)
		if W is not None:
			self.setTrefferModule(3, W)

	def setFrontLED(self, R=None, G=None, B=None, W=None):
		if R is not None:
			self.setLaserModule(3, R)
		if G is not None:
			self.setLaserModule(4, G)
		if B is not None:
			self.setLaserModule(5, B)
		if W is not None:
			self.setLaserModule(6, W)

			
if __name__ == '__main__':
	import time

	logging.basicConfig(level=logging.DEBUG)
	hardware = Hardware()
	
	hardware.setTopLED(R=255, G=0, B=0, W=0)
	time.sleep(0.5)
	hardware.setTopLED(R=0, G=255, B=0, W=0)
	time.sleep(0.5)
	hardware.setTopLED(R=0, G=0, B=255, W=0)
	time.sleep(0.5)
	hardware.setTopLED(R=0, G=0, B=0, W=0)
	
	hardware.setFrontLED(R=255, G=0, B=0, W=0)
	time.sleep(0.5)
	hardware.setFrontLED(R=0, G=255, B=0, W=0)
	time.sleep(0.5)
	hardware.setFrontLED(R=0, G=0, B=255, W=0)
	time.sleep(0.5)
	hardware.setFrontLED(R=0, G=0, B=0, W=0)
	
	hardware.setLaser(R=1)
	time.sleep(1)
	hardware.setLaser(R=0)
