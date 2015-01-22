#import logging
import time
import pygame

pygame.mixer.pre_init(44100, -16, 1, 512)
import display
import Sounds
import Hardware
import network
end = 9999999999999999999999999999999

i = 0
FireButton = 0
leben = 0

sounds = Sounds.Sounds()
hardware = Hardware.Hardware()
#cs = network.Client_server("10.0.8.200", 9005)

pygame.init()

hardware.setTopLED(G=255)
hardware.setIR_TX(id=32, dmg=30)#randint(1,254)

try:
	while True:
		#print network.Client_server.empf()
		leben = hardware.getLive()
		FireButton = hardware.getFireButton() 
		playerid, dmg = hardware.getLmHit()
		print playerid
		if playerid != 32 and playerid != 0:
			hardware.setTopLED(G=0)
			cs.send("death")
			sounds.play('tod', True)
			sounds.play('down', True)
			hardware.setTopLED(G=255)
			hardware.getLmHit() # Einmal abrufen fals man nochmal getroffen wurde
			FireButton = 0
			leben = 0
		
		if FireButton == 1 and display.schuss >=0:
			sounds.play('pew')
			hardware.setFireButton()
			hardware.setLaser(R=1)
			hardware.setFrontLED(R=2)
			time.sleep(0.1)
			hardware.setLaser(R=0)
			hardware.setFrontLED(R=0, B=0)
			i= i+1
			display.schuss = display.schuss-1
		if time.time() >= end:
			break
		print FireButton, i, display.schuss, leben
except KeyboardInterrupt:
	print 'Keyboard interrupt...'
	hardware.setLaser(R=0)
	hardware.setTopLED(R=0, G=0, B=0, W=0)
	hardware.setFrontLED(R=0, G=0, B=0, W=0)
	pygame.quit()
