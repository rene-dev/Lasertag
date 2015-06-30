import time
import pygame
import display
import sounds
import hardware
from hardware import i2cAddresses
import network
from enum import Enum

class ClientState(Enum):
	IDLE = 0
	SHOOTING = 1
	COOLDOWN = 2
	DEAD = 3

class Client:
	def __init__(self, pygame_instance):
		self.pygame = pygame_instance
		
		#config
		self.myid = 32
		self.health = 100.0
		self.ammo = 1000
		self.shotDuration = 100 #milliseconds
		self.cooldownDuration = 400 #milliseconds
		self.deathDuration = 5000 #milliseconds
		
		#runtime state
		self.shotEnd = 0
		self.cooldownEnd = 0
		self.deathEnd = 0
		self.state = ClientState.IDLE
		self.sounds = sounds.Sounds(self.pygame)
		self.display = display.Display(self.pygame, self.health, self.ammo)
		self.hardware = hardware.Hardware()
		#self.cs = network.Client_server("10.0.8.200", 9005)

		#initialize hardware
		self.hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 255, 0)
		self.hardware.setWeaponCharacteristics(playerid=32, damage=30, laser_duration=self.shotDuration/100)

	def shoot(self):
		if self.ammo > 0:
			self.state = ClientState.SHOOTING
			self.shotEnd = self.milliseconds + self.shotDuration
			self.ammo = self.ammo - 1
			self.display.setAmmo(self.ammo)
			self.sounds.play('pew')
			self.hardware.shootWeapon(laser0=1, laser1=0);
	
	def handleDeath(self):
		enable, playerid, dmg = self.hardware.getWeaponHitResults()
		if enable and playerid != self.myid:
			self.state = ClientState.DEAD
			self.deathEnd = self.milliseconds + self.deathDuration
			print "killed by player ", playerid
			#self.cs.send("death")
			self.sounds.play('tod')
			self.hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 0, 0)

	def update(self):
		self.milliseconds = self.pygame.time.get_ticks()
		
		#print network.Client_server.empf() where should this go?
		
		#state machine
		if self.state == ClientState.IDLE:
			if self.hardware.isWeaponButtonDown(0):
				self.shoot()
			self.handleDeath()
			
		elif self.state == ClientState.SHOOTING:
			#go back to idle state if the shot is over
			if self.milliseconds >= self.shotEnd:
				self.state = ClientState.COOLDOWN
				self.cooldownEnd = self.milliseconds + self.cooldownDuration
				#TODO: reset hardware here later!
			self.handleDeath()
			
		elif self.state == ClientState.COOLDOWN:
			if self.milliseconds >= self.cooldownEnd:
				self.state = ClientState.IDLE
			self.handleDeath()
			
		elif self.state == ClientState.DEAD:
			#reset hardware and jump to idle state
			if self.milliseconds >= self.deathEnd:
				self.state = ClientState.IDLE
				self.hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 255, 0)
				self.hardware.getWeaponHitResults() # flush in case of another hit

		self.display.redraw()

	def shutdown(self):
		print 'Shutting down...'
		self.hardware.setWeaponLasers(laser0=0, laser1=0)
		self.hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 0, 0)
		self.hardware.setWeaponLED(0, 0, 0, 0)

if __name__ == '__main__':
	pygame.mixer.pre_init(44100, -16, 1, 512)
	pygame.init()
	
	client = Client(pygame)
	try:
		while True:
			client.update()
	except KeyboardInterrupt:
		client.shutdown()
	
	pygame.quit()
