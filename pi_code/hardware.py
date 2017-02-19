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
	LED_R = 0					#OUTPUT, Front-RGBW-LED: [0, 255]
	LED_G = 1					#OUTPUT, Front-RGBW-LED: [0, 255]
	LED_B = 2					#OUTPUT, Front-RGBW-LED: [0, 255]
	LED_W = 3					#OUTPUT, Front-RGBW-LED: [0, 255]
	LASER = 4					#OUTPUT, Laser (Platinenbeschriftung "Laser 2"): [0, 1]
	VIBRATION = 7				#OUTPUT, Vibrationsmotor (Platinenbeschriftung "Laser 1"): [0, 255] VORSICHT!
	BUTTON0 = 10				#INPUT,  Button
	BUTTON1 = 11				#INPUT,  Button
	BUTTON2 = 12				#INPUT,  Button
	SHOOT_ENABLED = 20			#OUTPUT, Fur Schuss auf 1 setzen, setzt sich selbst zuruck: [0, 1]
	SHOOT_PLAYERID = 21			#OUTPUT, Wird bei Schuss per IR gesendet: [0, 255]
	SHOOT_DAMAGE = 22			#OUTPUT, Wird bei Schuss per IR gesendet: [0, 255]
	SHOOT_LASER = 23			#OUTPUT, Laser an bei Schuss: [0, 1]
	SHOOT_LASER_DURATION = 24	#OUTPUT, Laser wie lange an bei Schuss: [0, 255] Einheit??
	SHOOT_VIBRATE_POWER = 25	#OUTPUT, Vibrationsmotor wie stark an bei Schuss, 0 == garnicht: [0, 255] VORSICHT!
	SHOOT_VIBRATE_DURATION = 26	#OUTPUT, Vibrationsmotor wie lange an bei Schuss: [0, 255] Einheit??
	SHOOT_MUZZLE_FLASH_R = 27	#OUTPUT, Front-RGBW-LED Helligkeit bei Schuss: [0, 255]
	SHOOT_MUZZLE_FLASH_G = 28	#OUTPUT, Front-RGBW-LED Helligkeit bei Schuss: [0, 255]
	SHOOT_MUZZLE_FLASH_B = 29	#OUTPUT, Front-RGBW-LED Helligkeit bei Schuss: [0, 255]
	SHOOT_MUZZLE_FLASH_W = 30	#OUTPUT, Front-RGBW-LED Helligkeit bei Schuss: [0, 255]
	SHOOT_MUZZLE_FLASH_DURATION = 31	#OUTPUT, Front-RGBW-LED wie lange an bei Schuss: [0, 255] Einheit??
	HIT_ENABLE = 40				#INPUT,  1 wenn getroffen, setzt sich bei Auslesen auf 0 zuruck: [0, 1]
	HIT_PLAYERID = 41			#INPUT,  PlayerID des Schutzen: [0, 255]
	HIT_DMG = 42				#INPUT,  Angerichteter Schaden: [0, 255]
	V_BAT_L = 50				#INPUT,  Akkustand 16-Bit Wert zusammen mit V_BAT_R: [0, 255]
	V_BAT_R = 51				#INPUT,  Akkustand 16-Bit Wert zusammen mit V_BAT_L: [0, 255]
	LDR_L = 52					#INPUT,  Helligkeit 16-Bit Wert zusammen mit LDR_R: [0, 255]
	LDR_R = 53					#INPUT,  Helligkeit 16-Bit Wert zusammen mit LDR_L: [0, 255]

class hitpointRegisters(Enum):
	VIBRATION = 7				#OUTPUT, Vibrationsmotor: [0, 255] Noch nicht in Hardware vorhanden.
	HIT_ENABLE = 30				#INPUT,  1 wenn getroffen, setzt sich bei Auslesen auf 0 zuruck: [0, 1]
	HIT_PLAYERID = 31			#INPUT,  PlayerID des Schutzen: [0, 255]
	HIT_DMG = 32				#INPUT,  Angerichteter Schaden: [0, 255]
	LED_R = 50					#OUTPUT, 4 RGB-LEDs: [0, 255]
	LED_G = 51					#OUTPUT, 4 RGB-LEDs: [0, 255]
	LED_B = 52					#OUTPUT, 4 RGB-LEDs: [0, 255]

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
			except TypeError:
				pass
				#print("TYPEERROR", i2c_adr, register, data)
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

	def getWeaponVBat(self):
		links =  self.read(i2cAddresses.WEAPON, weaponRegisters.V_BAT_L)
		rechts = self.read(i2cAddresses.WEAPON, weaponRegisters.V_BAT_R)
		#return links<<8 | rechts
		return links*256 + rechts

	def getWeaponLDR(self):
		links =  self.read(i2cAddresses.WEAPON, weaponRegisters.LDR_L)
		rechts = self.read(i2cAddresses.WEAPON, weaponRegisters.LDR_R)
		return links*256 + rechts

	def setWeaponCharacteristics(self, playerid, damage, laser, laser_duration, vibrate_power, vibrate_duration, muzzle_flash_r, muzzle_flash_g, muzzle_flash_b, muzzle_flash_w, muzzle_flash_duration):
		print("playerid {0}; damage {1}; laser {2}; laser_duration {3}; vibrate_power {4}; vibrate_duration {5}; muzzle_flash_r {6}; muzzle_flash_b {7}; muzzle_flash_w {8}, muzzle_flash_duration {9}".format(playerid, damage, laser, laser_duration, vibrate_power, vibrate_duration, muzzle_flash_r, muzzle_flash_g, muzzle_flash_b, muzzle_flash_w, muzzle_flash_duration))
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
	hardware.setWeaponCharacteristics(playerid=42, damage=123, laser=1, laser_duration=10, vibrate_power=0, vibrate_duration=0, muzzle_flash_r=5, muzzle_flash_g=0, muzzle_flash_b=0, muzzle_flash_w=0, muzzle_flash_duration=25)
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

	print("V_Bat: " + str(hardware.getWeaponVBat()))

	print("V_LDR: " + str(hardware.getWeaponLDR()))
