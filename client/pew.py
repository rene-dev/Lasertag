import time

import pygame
pygame.init()

pygame.mixer.pre_init(44100, -16, 1, 512)
import sounds
sounds = sounds.Sounds()

import hardware
hardware = hardware.Hardware()

while True:
	try:
		if hardware.getWaffeButton(0) ==1:
			sounds.play('pew', False)
			hardware.setWaffeShoot(enable=1, playerid=123, damage=42, laser_dauer=1, laser_r=1, laser_g=0, laser_b=0)
			time.sleep(0.3)
		time.sleep(0.005)
	except IOError:
		pass
