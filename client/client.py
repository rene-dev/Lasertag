#import logging
import time
import pygame

pygame.mixer.pre_init(44100, -16, 1, 512)
import display
import sounds
import hardware
import network
myid = 32
i = 0
fireButton = 0

sounds = sounds.Sounds()
hardware = hardware.Hardware()
from hardware import i2cAddresses
#cs = network.Client_server("10.0.8.200", 9005)

pygame.init()

hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 255, 0)
hardware.setWeaponCharacteristics(playerid=32, damage=30, laser_duration=1)#randint(1,254)

try:
	while True:
		#print network.Client_server.empf()
		fireButton = hardware.isWeaponButtonDown(0) 
		enable, playerid, dmg = hardware.getWeaponHitResults()
		if enable and playerid != myid:
			print playerid
			hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 0, 0)
			#cs.send("death")
			sounds.play('tod', True)
			sounds.play('down', True)
			hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 255, 0)
			hardware.getWeaponHitResults() # flush in case of another hit
			fireButton = 0
		
		if fireButton == 1 and display.schuss >=0:
			sounds.play('pew')
			hardware.setWeaponLasers(laser0=1, laser1=0)
			hardware.setWeaponLED(2, 0, 0)
			time.sleep(0.1)
			hardware.setWeaponLasers(laser0=0, laser1=0)
			hardware.setWeaponLED(0, 0, 0)
			i= i+1
			display.schuss = display.schuss-1
		print fireButton, i, display.schuss
except KeyboardInterrupt:
	print 'Keyboard interrupt...'
	hardware.setWeaponLasers(laser0=0, laser1=0)
	hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 0, 0)
	hardware.setWeaponLED(0, 0, 0)
	pygame.quit()
