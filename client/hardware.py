#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import logging
import smbus
from enum import Enum

class i2cAddresses(Enum):
	BROADCAST = 0x00
	WEAPON = 0x03
	HITPOINT_WEAPON = 0x04
	HITPOINT0 = 0x04
	HITPOINT1 = 0x05
	HITPOINT2 = 0x06
	HITPOINT3 = 0x07
	HITPOINT4 = 0x08

class weaponRegisters(Enum):
	LED_R = 0
	LED_G = 1
	LED_B = 2
	LED_W = 3
	LASER_R = 4
	LASER_G = 5
	LASER_B = 6
	VIBRATION = 7
	BUTTON0 = 10
	BUTTON1 = 11
	BUTTON2 = 12
	SHOOT_ENABLED = 20
	SHOOT_PLAYERID = 21
	SHOOT_DAMAGE = 22
	SHOOT_DURATION = 23
	LASER0 = 24
	LASER1 = 25
	HIT_ENABLE = 30
	HIT_PLAYERID = 31
	HIT_DMG = 32
	V_BATT = 40
	V_BATT = 41
	LDR = 42
	LDR = 43

class hitpointRegisters(Enum):
	VIBRATION = 7
	HIT_ENABLE = 30
	HIT_PLAYERID = 31
	HIT_DMG = 32
	LED_R = 50
	LED_G = 51
	LED_B = 52

logger = logging.getLogger(__name__)

class Hardware:
	def __init__(self):
		self.connect()
		self.setWeaponLasers(0, 0)
		self.setWeaponLED(R=0, G=0, B=0, W=0)
		self.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, R=0, G=0, B=0)
		
	#----------------- low level -----------------
	def connect(self):
		try:
			self.bus = smbus.SMBus(0) #alte PIs
		except:
			self.bus = smbus.SMBus(1) #neuere PIs
			
	def disconnect(self):
		del self.bus
		
	def reconnect(self):
		self.disconnect()
		self.connect()

	def read(self, i2c_adr, register):
		while True:
			try:
				return self.bus.read_byte_data(i2c_adr, register)
			except IOError:
				self.reconnect()
				#print "i2c reopened"

	def write(self, i2c_adr, register, data):
		while True:
			try:
				self.bus.write_byte_data(i2c_adr, register, data)
				break
			except IOError:
				self.reconnect()
				#print "i2c reopened"

	#----------------- Lasermodul -----------------

	def isWeaponButtonDown(self, button):
		return self.read(i2cAddresses.WEAPON, weaponRegisters.BUTTON0 + button) == 1

	def getWeaponHitResults(self):
		playerid =	self.read(i2cAddresses.WEAPON, weaponRegisters.HIT_PLAYERID)
		damage =	self.read(i2cAddresses.WEAPON, weaponRegisters.HIT_DMG)
		enable =	self.read(i2cAddresses.WEAPON, weaponRegisters.HIT_ENABLE) != 0
		return (enable, playerid, damage)

	def getWeaponVBatt(self):
		links =  self.read(i2cAddresses.WEAPON, weaponRegisters.V_BATT)
		rechts = self.read(i2cAddresses.WEAPON, weaponRegisters.V_BATT)
		#return links<<8 | rechts
		return links*256 + rechts

	def getWeaponLDR(self):
		links =  self.read(i2cAddresses.WEAPON, weaponRegisters.LDR)
		rechts = self.read(i2cAddresses.WEAPON, weaponRegisters.LDR)
		return links*256 + rechts

	def setWeaponCharacteristics(self, playerid, damage, laser_duration):
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_PLAYERID, playerid)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_DAMAGE, damage)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_DURATION, laser_duration)

	def shootWeapon(self, laser0, laser1):
		self.setWeaponLasers(laser0, laser1)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_ENABLED, 1)

	def setWeaponLED(self, R, G, B, W):
		self.write(i2cAddresses.WEAPON, weaponRegisters.LED_R, R)
		self.write(i2cAddresses.WEAPON, weaponRegisters.LED_G, G)
		self.write(i2cAddresses.WEAPON, weaponRegisters.LED_B, B)
		self.write(i2cAddresses.WEAPON, weaponRegisters.LED_W, W)

	def setWeaponLasers(self, laser0, laser1):
		self.write(i2cAddresses.WEAPON, weaponRegisters.LASER0, laser0)
		self.write(i2cAddresses.WEAPON, weaponRegisters.LASER1, laser1)

	#----------------- Trefferzonenmodul -----------------

	def getHitpointResults(self, hitpoint_address):
		playerid =	self.read(hitpoint_address, hitpointRegisters.HIT_PLAYERID)
		damage =	self.read(hitpoint_address, hitpointRegisters.HIT_DMG)
		enable =	self.read(hitpoint_address, hitpointRegisters.HIT_ENABLE) != 0
		return (enable, playerid, damage)

	def setHitpointLED(self, hitpoint_address, R, G, B):
		self.write(hitpoint_address, hitpointRegisters.LED_R, R)
		self.write(hitpoint_address, hitpointRegisters.LED_G, G)
		self.write(hitpoint_address, hitpointRegisters.LED_B, B)

	#-----------------  -----------------

if __name__ == '__main__':
	import time

	logging.basicConfig(level=logging.DEBUG)
	hardware = Hardware()

	print("Waffe LED Front")
	hardware.setWeaponLED(R=50, G=0, B=0, W=0)
	time.sleep(0.5)
	hardware.setWeaponLED(R=0, G=50, B=0, W=0)
	time.sleep(0.5)
	hardware.setWeaponLED(R=0, G=0, B=50, W=0)
	time.sleep(0.5)
	hardware.setWeaponLED(R=0, G=0, B=0, W=50)
	time.sleep(0.5)
	hardware.setWeaponLED(R=0, G=0, B=0, W=0)
	time.sleep(0.5)

	print("Waffe LED Top")
	hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, R=100, G=0, B=0)
	time.sleep(0.5)
	hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, R=0, G=100, B=0)
	time.sleep(0.5)
	hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, R=0, G=0, B=100)
	time.sleep(0.5)
	hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, R=0, G=0, B=0)
	time.sleep(0.5)

	print("Waffe Laser")
	hardware.setWeaponLasers(laser0=1, laser1=0)
	time.sleep(0.5)
	hardware.setWeaponLasers(laser0=0, laser1=1)
	time.sleep(0.5)
	hardware.setWeaponLasers(laser0=0, laser1=0)
	time.sleep(1.5)
	
	enable, playerid, damage = hardware.getWeaponHitResults()
	print("Waffe Hit Front enable: " + str(enable))
	print("Waffe Hit Front playerid: " + str(playerid))
	print("Waffe Hit Front damage: " + str(damage))

	enable, playerid, damage = hardware.getHitpointResults(i2cAddresses.HITPOINT_WEAPON)
	print("Waffe Hit Top enable: " + str(enable))
	print("Waffe Hit Top playerid: " + str(playerid))
	print("Waffe Hit Top damage: " + str(damage))

	print("Waffe Shoot: playerid=123, damage=5, rot")
	#dauer in 0.1s
	hardware.setWeaponCharacteristics(playerid=123, damage=42, laser_duration=5)
	hardware.shootWeapon(laser0 = 1, laser1 = 0)
	time.sleep(0.5)

	print("Waffe Button 0: " + str(hardware.isWeaponButtonDown(0)))
	print("Waffe Button 1: " + str(hardware.isWeaponButtonDown(1)))
	print("Waffe Button 2: " + str(hardware.isWeaponButtonDown(2)))

	enable, playerid, damage = hardware.getWeaponHitResults()
	print("Waffe Hit Front enable: " + str(enable))
	print("Waffe Hit Front playerid: " + str(playerid))
	print("Waffe Hit Front damage: " + str(damage))

	enable, playerid, damage = hardware.getHitpointResults(i2cAddresses.HITPOINT_WEAPON)
	print("Waffe Hit Top enable: " + str(enable))
	print("Waffe Hit Top playerid: " + str(playerid))
	print("Waffe Hit Top damage: " + str(damage))

	print("V_Batt: " + str(hardware.getWeaponVBatt()))

	print("V_LDR: " + str(hardware.getWeaponLDR()))
