#import logging
import time

import hardware
hardware = hardware.Hardware()

hardware.setWaffeShoot(playerid=123, damage=42, laser_dauer=2, laser_r=1, laser_g=0, laser_b=0)
	
while True:
	print("Waffe Shoot: playerid=123, damage=5, rot")
	#dauer in 0.1s
	hardware.setWaffeShoot(enable=1)
	time.sleep(1)
