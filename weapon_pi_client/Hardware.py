#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import logging
import smbus

logger = logging.getLogger(__name__)

class Hardware:
	adrWaffeLm = 1
	adrWaffeTm = 2

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

	def getWaffeKey(self, key=0):
		return self.getData(self.adrWaffeLm, 10+key)

	def getWaffeHitFront(self):
		playerid =	self.getData(self.adrWaffeLm, 31)
		dmg =		self.getData(self.adrWaffeLm, 32)
		enable =	self.getData(self.adrWaffeLm, 30)
		return (enable, playerid, dmg)

	def getWaffeVBatt(self):
		links =  self.getData(self.adrWaffeLm, 40)
		rechts = self.getData(self.adrWaffeLm, 41)
		return links.append(rechts)
		
	def getWaffeLDR(self):
		links =  self.getData(self.adrWaffeLm, 42)
		rechts = self.getData(self.adrWaffeLm, 43)
		return links.append(rechts)
		
	def setWaffeShoot(self, enable=None, playerid=None, dmg=None, laser_dauer=None, laser_r=0, laser_g=0, laser_b=0):
		if playerid is not None:
			self.bus.write_byte_data(self.adrWaffeLm, 21, 1)
		if dmg is not None:
			self.bus.write_byte_data(self.adrWaffeLm, 22, 1)
		if laser_dauer is not None:
			self.bus.write_byte_data(self.adrWaffeLm, 23, 1)
		self.setWaffeLaser(laser_r, laser_g, laser_b)
		if enable is not None:
			self.bus.write_byte_data(self.adrWaffeLm, 20, 1)

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
		dmg =		self.getData(self.adrWaffeTm, 32)
		enable =	self.getData(self.adrWaffeTm, 30)
		return (enable, playerid, dmg)
	
	def setWaffeLEDTop(self, R=None, G=None, B=None, W=None):
		if R is not None:
			self.setData(self.adrWaffeTm, 53, R)
		if G is not None:
			self.setData(self.adrWaffeTm, 54, G)
		if B is not None:
			self.setData(self.adrWaffeTm, 55, B)

	#-----------------  -----------------
			
if __name__ == '__main__':
	import time

	logging.basicConfig(level=logging.DEBUG)
	hardware = Hardware()
	
	print("Waffe LED Front")
	hardware.setWaffeLEDFront(R=255, G=0, B=0, W=0)
	time.sleep(0.5)
	hardware.setWaffeLEDFront(R=0, G=255, B=0, W=0)
	time.sleep(0.5)
	hardware.setWaffeLEDFront(R=0, G=0, B=255, W=0)
	time.sleep(0.5)
	hardware.setWaffeLEDFront(R=0, G=0, B=0, W=255)
	time.sleep(0.5)
	hardware.setWaffeLEDFront(R=0, G=0, B=0, W=0)
	time.sleep(0.5)
	
	print("Waffe LED Top")
	hardware.setWaffeLEDTop(R=255, G=0, B=0)
	time.sleep(0.5)
	hardware.setWaffeLEDTop(R=0, G=255, B=0)
	time.sleep(0.5)
	hardware.setWaffeLEDTop(R=0, G=0, B=255)
	time.sleep(0.5)
	hardware.setWaffeLEDTop(R=0, G=0, B=0)
	time.sleep(0.5)

	print("Waffe Laser")
	hardware.setWaffeLaser(R=255, G=0, B=0)
	time.sleep(0.5)
	hardware.setWaffeLaser(R=0, G=255, B=0)
	time.sleep(0.5)
	hardware.setWaffeLaser(R=0, G=0, B=255)
	time.sleep(0.5)
	hardware.setWaffeLaser(R=0, G=0, B=0)
	time.sleep(0.5)

	print("Waffe Shoot: playerid=123, dmg=42, rot")
	hardware.setWaffeShoot(enable=1, playerid=123, dmg=42, laser_dauer=100, laser_r=1, laser_g=0, laser_b=0)
	time.sleep(1)

	print("Waffe Key 0: "+getWaffeKey(0))
	print("Waffe Key 1: "+getWaffeKey(1))
	print("Waffe Key 2: "+getWaffeKey(2))

	enable, playerid, dmg = getWaffeHitFront(self):
	print("Waffe Hit Front enable: "+enable)
	print("Waffe Hit Front playerid: "+playerid)
	print("Waffe Hit Front dmg: "+dmg)

	enable, playerid, dmg = getWaffeHitTop(self):
	print("Waffe Hit Top enable: "+enable)
	print("Waffe Hit Top playerid: "+playerid)
	print("Waffe Hit Top dmg: "+dmg)

	print("V_Batt: "getWaffeVBatt())

	print("V_Batt: "getWaffeLDR())
