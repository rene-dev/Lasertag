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
	LASER = 4 #Laser 2, AN_AUS
	VIBRATION = 7 #Laser 1, PWM_8_BIT
	BUTTON0 = 10
	BUTTON1 = 11
	BUTTON2 = 12
	SHOOT_ENABLED = 20
	SHOOT_PLAYERID = 21
	SHOOT_DAMAGE = 22
	SHOOT_LASER = 23
	SHOOT_LASER_DURATION = 24
	SHOOT_VIBRATE_POWER = 25
	SHOOT_VIBRATE_DURATION = 26
	SHOOT_MUZZLE_FLASH_R = 27
	SHOOT_MUZZLE_FLASH_G = 28
	SHOOT_MUZZLE_FLASH_B = 29
	SHOOT_MUZZLE_FLASH_W = 30
	SHOOT_MUZZLE_FLASH_DURATION = 31
	HIT_ENABLE = 40
	HIT_PLAYERID = 41
	HIT_DMG = 42
	V_BATT = 50
	V_BATT = 51
	LDR = 52
	LDR = 53

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
		self.setWeaponLasers(laser=0)
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

	def setWeaponCharacteristics(self, playerid, damage, laser, laser_duration, vibrate_power, vibrate_duration, muzzle_flash_r, muzzle_flash_g, muzzle_flash_b, muzzle_flash_w, muzzle_flash_duration):
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_PLAYERID, playerid)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_DAMAGE, damage)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_LASER, laser)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_LASER_DURATION, laser_duration)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_VIBRATE_POWER, vibrate_power)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_VIBRATE_DURATION, vibrate_duration)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_MUZZLE_FLASH_R, muzzle_flash_r)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_MUZZLE_FLASH_G, muzzle_flash_g)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_MUZZLE_FLASH_B, muzzle_flash_b)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_MUZZLE_FLASH_W, muzzle_flash_w)
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_MUZZLE_FLASH_DURATION, muzzle_flash_duration)

	def shootWeapon(self):
		self.write(i2cAddresses.WEAPON, weaponRegisters.SHOOT_ENABLED, 1)

	def setWeaponLED(self, R, G, B, W):
		self.write(i2cAddresses.WEAPON, weaponRegisters.LED_R, R)
		self.write(i2cAddresses.WEAPON, weaponRegisters.LED_G, G)
		self.write(i2cAddresses.WEAPON, weaponRegisters.LED_B, B)
		self.write(i2cAddresses.WEAPON, weaponRegisters.LED_W, W)

	def setWeaponLasers(self, laser):
		self.write(i2cAddresses.WEAPON, weaponRegisters.LASER, laser)

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

	# print("Waffe LED Front")
	# hardware.setWeaponLED(R=20, G=0, B=0, W=0)
	# time.sleep(0.5)
	# hardware.setWeaponLED(R=0, G=20, B=0, W=0)
	# time.sleep(0.5)
	# hardware.setWeaponLED(R=0, G=0, B=20, W=0)
	# time.sleep(0.5)
	# hardware.setWeaponLED(R=0, G=0, B=0, W=20)
	# time.sleep(0.5)
	# hardware.setWeaponLED(R=0, G=0, B=0, W=0)
	# time.sleep(0.5)

	# print("Waffe LED Top")
	# hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, R=100, G=0, B=0)
	# time.sleep(0.5)
	# hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, R=0, G=100, B=0)
	# time.sleep(0.5)
	# hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, R=0, G=0, B=100)
	# time.sleep(0.5)
	# hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, R=0, G=0, B=0)
	# time.sleep(0.5)

	# print("Waffe Laser")
	# hardware.setWeaponLasers(laser=1)
	# time.sleep(0.5)
	# hardware.setWeaponLasers(laser=0)
	# time.sleep(0.5)
	
	enable, playerid, damage = hardware.getWeaponHitResults()
	print("Waffe Hit Front enable: " + str(enable))
	print("Waffe Hit Front playerid: " + str(playerid))
	print("Waffe Hit Front damage: " + str(damage))

	enable, playerid, damage = hardware.getHitpointResults(i2cAddresses.HITPOINT_WEAPON)
	print("Waffe Hit Top enable: " + str(enable))
	print("Waffe Hit Top playerid: " + str(playerid))
	print("Waffe Hit Top damage: " + str(damage))

	print("Waffe Shoot: playerid=42, damage=123")
	#dauer in 0.1s
	hardware.setWeaponCharacteristics(playerid=42, damage=123, laser=1, laser_duration=10, vibrate_power=0, vibrate_duration=0, muzzle_flash_r=5, muzzle_flash_g=0, muzzle_flash_b=0, muzzle_flash_w=0, muzzle_flash_duration=20)
	# hardware.shootWeapon()
	# time.sleep(0.1)
	# hardware.shootWeapon()
	# time.sleep(0.1)
	hardware.shootWeapon()
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
