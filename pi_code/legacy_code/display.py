import time
import pygame

class Display:
	def __init__(self, pygame_instance, health, ammo):
		self.pygame = pygame_instance
		self.pygame.mouse.set_visible(False)
		self.screen = self.pygame.display.set_mode([240, 320])
		self.font1 = self.pygame.font.SysFont("comicsansms", 72)
		self.font2 = self.pygame.font.SysFont("comicsansms", 25)
		self.sprite_weapon = self.pygame.image.load("images/waffe.jpg")
		self.sprite_heart = self.pygame.image.load("images/herz.png")
		
		self.last_clock = ""
		self.setHealth(health)
		self.setAmmo(ammo)
		
	def setAmmo(self, ammo):
		self.text_ammo = self.font1.render(str(ammo), True, (0, 128, 0))
		
	def setHealth(self, health):
		self.text_health = self.font1.render(str(health), True, (0,128,0))

	def redraw(self):
		# update clock text
		current_clock = str(time.strftime("%H:%M:%S"))
		if current_clock != self.last_clock:
			self.text_clock = self.font2.render(current_clock, True, (0, 255,0))
			self.last_clock = current_clock
	
		# clear and redraw everything
		self.screen.fill((255, 255, 255))
		self.pygame.draw.rect(self.screen,[0,0,0],[0,0,240,17],0)
		self.pygame.draw.rect(self.screen,[0,255,0],[5,5,3,10],0)
		self.pygame.draw.rect(self.screen,[0,255,0],[10,8,3,7],0)
		self.pygame.draw.rect(self.screen,[0,255,0],[15,12,3,3],0)
		self.pygame.draw.rect(self.screen,[0,255,0],[0,70,240,3],0)
		self.pygame.draw.rect(self.screen,[0,255,0],[0,120,240,3],0)
		self.screen.blit(self.sprite_weapon, (0, 30))
		self.screen.blit(self.sprite_heart, (0, 75))
		self.screen.blit(self.text_ammo, (100 - self.text_ammo.get_width() // 2, 45 - self.text_ammo.get_height() // 2))
		self.screen.blit(self.text_health, (100 - self.text_health.get_width() // 2, 95 - self.text_health.get_height() // 2))
		self.screen.blit(self.text_clock, (175, 0))
		self.pygame.display.flip()
