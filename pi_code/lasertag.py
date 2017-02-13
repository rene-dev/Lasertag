import sys
import time
import pygame
import display
#import sounds
import hardware
from hardware import i2cAddresses
from enum import Enum
import networkserver
import networkclient
from twisted.internet import reactor

class PlayerRole(Enum):
	CLIENT = 0
	SERVER = 1

class PlayerState(Enum):
	IDLE = 0
	SHOOTING = 1
	COOLDOWN = 2
	DEAD = 3

class Lasertag:
	def __init__(self, pygame_instance, role, ip, port, name):
		self.pygame = pygame_instance

		#config
		self.myid = 0 # will be set by the server!
		self.health = 100.0
		self.ammo = 1000
		self.shotDuration = 100 #milliseconds
		self.cooldownDuration = 400 #milliseconds
		self.deathDuration = 5000 #milliseconds

		#runtime state
		self.shotEnd = 0
		self.cooldownEnd = 0
		self.deathEnd = 0
		self.state = PlayerState.IDLE
		#self.sounds = sounds.Sounds(self.pygame)
		self.display = display.Display(self.pygame, self.health, self.ammo)
		self.hardware = hardware.Hardware()
		self.role = role
		#TODO: if the player role is server: start the server in another thread and connect client via localhost!
		if role == PlayerRole.SERVER:
			reactor.listenTCP(port, networkserver.PlayerFactory())
			ip = "127.0.0.1" #always connect to our own server!
		self.networkclient = networkclient.NetworkClient()
		self.networkclient.connect(ip, port, name) #TODO: uh, we need to iterate the server reactor during this, right?

	def onPlayerIdReceived(self, playerid):
		self.myid = playerid

		#initialize hardware
		self.hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 255, 0)
		self.hardware.setWeaponCharacteristics(self.myid, 30, 0, self.shotDuration/100, 0, 0, 255, 0, 255, 127, 1)

	def shoot(self):
		if self.ammo > 0:
			self.state = PlayerState.SHOOTING
			self.shotEnd = self.milliseconds + self.shotDuration
			self.ammo = self.ammo - 1
			self.display.setAmmo(self.ammo)
			#self.sounds.play('pew')
			self.hardware.shootWeapon()

	def handleHit(self, enable, playerid, dmg, sourceName):
		if enable and playerid != self.myid:
			self.state = PlayerState.DEAD
			self.deathEnd = self.milliseconds + self.deathDuration
			print "hit by player ", playerid, " at module: ", sourceName
			self.networkclient.sendHitEvent(playerid)
			#self.sounds.play('tod')
			self.hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 0, 0)

	def handleHits(self):
		enable, playerid, dmg = self.hardware.getWeaponHitResults()
		self.handleHit(enable, playerid, dmg, "WEAPON")
		enable, playerid, dmg = self.hardware.getHitpointResults(i2cAddresses.HITPOINT_WEAPON)
		self.handleHit(enable, playerid, dmg, "HITPOINT_WEAPON")
		#TODO: loop over all hitpoints here later!

	def update(self):
		self.milliseconds = self.pygame.time.get_ticks()

		#state machine
		if self.state == PlayerState.IDLE:
			if self.hardware.isWeaponButtonDown(0):
				self.shoot()
			self.handleHits()

		elif self.state == PlayerState.SHOOTING:
			#go back to idle state if the shot is over
			if self.milliseconds >= self.shotEnd:
				self.state = PlayerState.COOLDOWN
				self.cooldownEnd = self.milliseconds + self.cooldownDuration
				#TODO: reset hardware here later!
			self.handleHits()

		elif self.state == PlayerState.COOLDOWN:
			if self.milliseconds >= self.cooldownEnd:
				self.state = PlayerState.IDLE
			self.handleHits()

		elif self.state == PlayerState.DEAD:
			#reset hardware and jump to idle state
			if self.milliseconds >= self.deathEnd:
				self.state = PlayerState.IDLE
				self.hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 255, 0)
				# flush hits during death
				self.hardware.getWeaponHitResults()
				self.hardware.getHitpointResults(i2cAddresses.HITPOINT_WEAPON)

		#update stuff on the display
		self.display.redraw()

		#update/poll networking stuff
		print("Polling")
		self.networkclient.poll()
		if self.myid == 0: # if own playerid not yet set by the server
			self.onPlayerIdReceived(self.networkclient.getPlayerId())
		if self.role == PlayerRole.SERVER:
			reactor.iterate()

	def shutdown(self):
		print 'Shutting down...'
		self.networkclient.disconnect()
		self.hardware.setWeaponLasers()
		self.hardware.setHitpointLED(i2cAddresses.HITPOINT_WEAPON, 0, 0, 0)
		self.hardware.setWeaponLED(0, 0, 0, 0)

if __name__ == '__main__':
	# handle arguments
	role = PlayerRole.CLIENT
	if len(sys.argv) > 1:
            if sys.argv[1] == "server":
		role = PlayerRole.SERVER
	else:
		print "Usage: ", sys.argv[0], "<client|server>\n"

	# initialize pygame
	pygame.mixer.pre_init(44100, -16, 1, 512)
	pygame.init()

	# run a lasertag instance!
	lasertag = Lasertag(pygame, role, "127.0.0.1", 1234, "Rainbow crash") #testing params!
	try:
		while True:
			lasertag.update()
	except KeyboardInterrupt:
		lasertag.shutdown()

	# quit
	pygame.quit()
