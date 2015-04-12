#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import logging
import smbus

logger = logging.getLogger(__name__)

class Hardware:
	#i2c-bus adress
	#0x00				Broadcast
	#0x03				Weapon Lasermodule
	#0x04				Weapon Hitmodule
	#0x10, 0x11, ...	Weste Hitmodules
	adrWaffeLm = 0x03
	adrWaffeTm = 0x04

	def __init__(self):
		try:
			self.bus = smbus.SMBus(0) #alte PIs
		except:
			self.bus = smbus.SMBus(1) #neuere PIs
		self.setWaffeLaser(R=0, G=0, B=0)
		self.setWaffeLEDFront(R=0, G=0, B=0, W=0)
		self.setWaffeLEDTop(R=0, G=0, B=0)
	
	#----------------- low level -----------------
	
	def getData(self, i2c_adr, register):
		return self.bus.read_byte_data(i2c_adr, register)

	def setData(self, i2c_adr, register, data):
		self.bus.write_byte_data(i2c_adr, register, data)

	#----------------- Lasermodul -----------------

	def getWaffeButton(self, button=0):
		return self.getData(self.adrWaffeLm, 10 + button)

	def getWaffeHitFront(self):
		playerid =	self.getData(self.adrWaffeLm, 31)
		damage =	self.getData(self.adrWaffeLm, 32)
		enable =	self.getData(self.adrWaffeLm, 30)
		return (enable, playerid, damage)

	def getWaffeVBatt(self):
		links =  self.getData(self.adrWaffeLm, 40)
		rechts = self.getData(self.adrWaffeLm, 41)
		#return links<<8 | rechts
		return links*256 + rechts
  
	def getWaffeLDR(self):
		links =  self.getData(self.adrWaffeLm, 42)
		rechts = self.getData(self.adrWaffeLm, 43)
		return links*256 + rechts
		
	def setWaffeShoot(self, enable=None, playerid=None, damage=None, laser_dauer=None, laser_r=0, laser_g=0, laser_b=0):
		if playerid is not None:
			self.bus.write_byte_data(self.adrWaffeLm, 21, playerid)
		if damage is not None:
			self.bus.write_byte_data(self.adrWaffeLm, 22, damage)
		if laser_dauer is not None:
			self.bus.write_byte_data(self.adrWaffeLm, 23, laser_dauer)
		self.bus.write_byte_data(self.adrWaffeLm, 24, laser_r)
		self.bus.write_byte_data(self.adrWaffeLm, 25, laser_g)
		self.bus.write_byte_data(self.adrWaffeLm, 26, laser_b)
		#self.setWaffeLaser(laser_r, laser_g, laser_b)
		if enable is not None:
			self.bus.write_byte_data(self.adrWaffeLm, 20, enable)

	def setWaffeLEDFront(self, R=None, G=None, B=None, W=None):
		if R is not None:
			self.setData(self.adrWaffeLm, 0, R)
		if G is not None:
			self.setData(self.adrWaffeLm, 1, G)
		if B is not None:
			self.setData(self.adrWaffeLm, 2, B)
		if W is not None:
			self.setData(self.adrWaffeLm, 3, W)

	def setWaffeLaser(self, R=None, G=None, B=None):
		if R is not None:
			self.setData(self.adrWaffeLm, 4, R)
		if G is not None:
			self.setData(self.adrWaffeLm, 5, G)
		if B is not None:
			self.setData(self.adrWaffeLm, 6, B)

	#----------------- Trefferzonenmodul -----------------

	def getWaffeHitTop(self):
		playerid =	self.getData(self.adrWaffeTm, 31)
		damage =	self.getData(self.adrWaffeTm, 32)
		enable =	self.getData(self.adrWaffeTm, 30)
		return (enable, playerid, damage)
	
	def setWaffeLEDTop(self, R=None, G=None, B=None, W=None):
		if R is not None:
			self.setData(self.adrWaffeTm, 50, R)
		if G is not None:
			self.setData(self.adrWaffeTm, 51, G)
		if B is not None:
			self.setData(self.adrWaffeTm, 52, B)

	#-----------------  -----------------
			
if __name__ == '__main__':
	import time

	logging.basicConfig(level=logging.DEBUG)
	hardware = Hardware()
	
	print("Waffe LED Front")
	hardware.setWaffeLEDFront(R=50, G=0, B=0, W=0)
	time.sleep(0.5)
	hardware.setWaffeLEDFront(R=0, G=50, B=0, W=0)
	time.sleep(0.5)
	hardware.setWaffeLEDFront(R=0, G=0, B=50, W=0)
	time.sleep(0.5)
	hardware.setWaffeLEDFront(R=0, G=0, B=0, W=50)
	time.sleep(0.5)
	hardware.setWaffeLEDFront(R=0, G=0, B=0, W=0)
	time.sleep(0.5)
	
	print("Waffe LED Top")
	hardware.setWaffeLEDTop(R=100, G=0, B=0)
	time.sleep(0.5)
	hardware.setWaffeLEDTop(R=0, G=100, B=0)
	time.sleep(0.5)
	hardware.setWaffeLEDTop(R=0, G=0, B=100)
	time.sleep(0.5)
	hardware.setWaffeLEDTop(R=0, G=0, B=0)
	time.sleep(0.5)

	# print("Waffe Laser")
	# hardware.setWaffeLaser(R=1, G=0, B=0)
	# time.sleep(0.5)
	# hardware.setWaffeLaser(R=0, G=1, B=0)
	# time.sleep(0.5)
	# hardware.setWaffeLaser(R=0, G=0, B=1)
	# time.sleep(0.5)
	# hardware.setWaffeLaser(R=0, G=0, B=0)
	# time.sleep(1.5)

	print("Waffe Shoot: playerid=123, damage=5, rot")
	#dauer in 0.1s
	hardware.setWaffeShoot(enable=1, playerid=123, damage=42, laser_dauer=5, laser_r=1, laser_g=0, laser_b=0)
	time.sleep(0.5)

	print("Waffe Button 0: " + str(hardware.getWaffeButton(0)))
	print("Waffe Button 1: " + str(hardware.getWaffeButton(1)))
	print("Waffe Button 2: " + str(hardware.getWaffeButton(2)))

	enable, playerid, damage = hardware.getWaffeHitFront()
	print("Waffe Hit Front enable: " + str(enable))
	print("Waffe Hit Front playerid: " + str(playerid))
	print("Waffe Hit Front damage: " + str(damage))

	enable, playerid, damage = hardware.getWaffeHitTop()
	print("Waffe Hit Top enable: " + str(enable))
	print("Waffe Hit Top playerid: " + str(playerid))
	print("Waffe Hit Top damage: " + str(damage))

	print("V_Batt: " + str(hardware.getWaffeVBatt()))

	print("V_LDR: " + str(hardware.getWaffeLDR()))
