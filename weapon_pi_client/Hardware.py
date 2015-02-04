#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import logging
import smbus 

"""	addr 0x18
0		1		2		3		4		5		6		7		8		9		10		11		12		13				14
key_1	key_2	key_3	led_r	led_g	led_b	led_w	laser_r	laser_g	laser_b	tx_pid	tx_dmg	shoot	treffer_fertig	haptik
"""

logger = logging.getLogger(__name__)

class Hardware:
	adrTrefferModule = 0x10
	adrLaserModule = 0x18

	def __init__(self):
		self.bus = smbus.SMBus(1)
		self.getKey0()
		self.getLive()
		self.setLaser(R=0, G=0, B=0)
		self.setFrontLED(R=0, G=0, B=0, W=0)
		self.setTopLED(R=0, G=0, B=0, W=0)
	
	#----------------- low level -----------------
	
	def getLmData(self, register):
		return self.bus.read_byte_data(self.adrLaserModule, register)

	def setLmData(self, register, data):
		self.bus.write_byte_data(self.adrLaserModule, register, data)

	def getTmData(self, register):
		return self.bus.read_byte_data(self.adrTrefferModule, register)

	def setTmData(self, register, data):
		self.bus.write_byte_data(self.adrTrefferModule, register, data)
				
	#----------------- Lasermodul -----------------
				
	def setIR_TX(self, id=None, dmg=None):
		if id is not None:
			self.bus.write_byte_data(self.adrLaserModule, 10, id)
		if dmg is not None:
			self.bus.write_byte_data(self.adrLaserModule, 11, dmg)
	
	def getLmHit(self):
		playerid = self.getLmData(10)
		dmg = self.getLmData(11)
		self.bus.write_byte_data(self.adrLaserModule, 13, 1)
		return (playerid, dmg)
		
	#def getFireTreffer(self):
		
	def setShoot(self, enable=None, playerid=None, dmg=None, dauer=None, color=None):
		if enable is not None:
			self.bus.write_byte_data(self.adrLaserModule, 20, 1)
		if playerid is not None:
			self.bus.write_byte_data(self.adrLaserModule, 21, 1)
		if dmg is not None:
			self.bus.write_byte_data(self.adrLaserModule, 22, 1)
		if dauer is not None:
			self.bus.write_byte_data(self.adrLaserModule, 23, 1)
		if color is not None:
			self.bus.write_byte_data(self.adrLaserModule, 24, 1)
		
	def getKey0(self):
		return self.getLmData(10)
		
	def getKey1(self):
		return self.getLmData(11)
		
	def getKey2(self):
		return self.getLmData(12)

	#def getLive(self):
	#	return self.getTmData(0x10)

	def setTopLED(self, R=None, G=None, B=None, W=None):
		if R is not None:
			self.setTmData(0, R)
		if G is not None:
			self.setTmData(1, G)
		if B is not None:
			self.setTmData(2, B)
		if W is not None:
			self.setTmData(3, W)

	def setFrontLED(self, R=None, G=None, B=None, W=None):
		if R is not None:
			self.setLmData(0, R)
		if G is not None:
			self.setLmData(1, G)
		if B is not None:
			self.setLmData(2, B)
		if W is not None:
			self.setLmData(3, W)

	def setLaser(self, R=None, G=None, B=None):
		if R is not None:
			self.setLmData(4, R)
		if G is not None:
			self.setLmData(5, G)
		if B is not None:
			self.setLmData(6, B)

			
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
