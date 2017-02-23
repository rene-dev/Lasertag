import time

import pygame
pygame.mixer.pre_init(44100, -16, 1, 512) # must be called before pygame.init!!!
pygame.init()
import sounds
sounds = sounds.Sounds()

import hardware
hardware = hardware.Hardware()

hardware.setWeaponCharacteristics(playerid = 123, damage = 42, laser_duration = 1)
while True:
	if hardware.isWeaponButtonDown(0):
		sounds.play('pew', False)
		hardware.shootWeapon(laser0 = 1, laser1 = 0)
		time.sleep(0.3)
	time.sleep(0.005)
