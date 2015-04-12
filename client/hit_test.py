#import logging
import time

import hardware
hardware = hardware.Hardware()

while True:
	enable, playerid, damage = hardware.getWaffeHitFront()
	if enable:
		print("Waffe Hit Front enable: " + str(enable))
		print("Waffe Hit Front playerid: " + str(playerid))
		print("Waffe Hit Front damage: " + str(damage))
	enable, playerid, damage = hardware.getWaffeHitTop()
	if enable:
		print("Waffe Hit Top enable: " + str(enable))
		print("Waffe Hit Top playerid: " + str(playerid))
		print("Waffe Hit Top damage: " + str(damage))
