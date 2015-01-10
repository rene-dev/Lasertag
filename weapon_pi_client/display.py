import time
import pygame
import random
import thread

global schuss
schuss = 1000

pygame.init()
pygame.mouse.set_visible(False)
font = pygame.font.SysFont("comicsansms", 72)
klein = pygame.font.SysFont("comicsansms", 25)
screen = pygame.display.set_mode([240, 320])
bild = pygame.image.load("images/waffe.jpg")
herz = pygame.image.load("images/herz.png")
red = 255,0,0

def neu():
	i=0
	while 1:
		time.sleep(0.1)
		uhr=time.strftime("%H:%M:%S")
		text = font.render(str(schuss), True, (0, 128, 0))
		uhrzeit = klein.render(str(uhr), True, (0, 255,0))
		leben = font.render("100%", True, (0,128,0))
		screen.fill((255, 255, 255))
		pygame.draw.rect(screen,[0,0,0],[0,0,240,17],0)
		pygame.draw.rect(screen,[0,255,0],[5,5,3,10],0)
		pygame.draw.rect(screen,[0,255,0],[10,8,3,7],0)
		pygame.draw.rect(screen,[0,255,0],[15,12,3,3],0)
		pygame.draw.rect(screen,[0,255,0],[0,70,240,3],0)
		pygame.draw.rect(screen,[0,255,0],[0,120,240,3],0)
		screen.blit(bild, (0, 30))
		screen.blit(herz, (0, 75))
		screen.blit(text,(100 - text.get_width() // 2, 45 - text.get_height() // 2))
		screen.blit(leben,(100 - text.get_width() // 2, 95 - text.get_height() // 2))
		screen.blit(uhrzeit,(220 - text.get_width() // 2, 25 - text.get_height() // 2))
		pygame.display.update()

thread.start_new_thread(neu,())
