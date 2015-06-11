#import logging
import time

import hardware
hardware = hardware.Hardware()
from hardware import i2cAddresses

while True:
	enable, playerid, damage = hardware.getWeaponHitResults()
	if enable:
		print("Waffe Hit Front enable: " + str(enable))
		print("Waffe Hit Front playerid: " + str(playerid))
		print("Waffe Hit Front damage: " + str(damage))
	enable, playerid, damage = hardware.getHitpointResults(i2cAddresses.HITPOINT_WEAPON)
	if enable:
		print("Waffe Hit Top enable: " + str(enable))
		print("Waffe Hit Top playerid: " + str(playerid))
		print("Waffe Hit Top damage: " + str(damage))
