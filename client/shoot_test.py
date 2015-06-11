#import logging
import time

import hardware
hardware = hardware.Hardware()

hardware.setWeaponCharacteristics(playerid=123, damage=42, laser_duration=2)
	
while True:
	print(".")
	hardware.shootWeapon(laser0=1, laser1=0)
	time.sleep(1)
