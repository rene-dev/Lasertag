import time
import pygame
import random
import thread

global schuss
schuss = 1000

pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode([240, 320])
font1 = pygame.font.SysFont("comicsansms", 72)
font2 = pygame.font.SysFont("comicsansms", 25)
bild_waffe = pygame.image.load("images/waffe.jpg")
bild_herz = pygame.image.load("images/herz.png")

def neu():
	while 1:
		time.sleep(0.1)
		text_schuss = font1.render(str(schuss), True, (0, 128, 0))
		text_uhrzeit = font2.render(str(time.strftime("%H:%M:%S")), True, (0, 255,0))
		text_leben = font1.render("100%", True, (0,128,0))
		screen.fill((255, 255, 255))
		pygame.draw.rect(screen,[0,0,0],[0,0,240,17],0)
		pygame.draw.rect(screen,[0,255,0],[5,5,3,10],0)
		pygame.draw.rect(screen,[0,255,0],[10,8,3,7],0)
		pygame.draw.rect(screen,[0,255,0],[15,12,3,3],0)
		pygame.draw.rect(screen,[0,255,0],[0,70,240,3],0)
		pygame.draw.rect(screen,[0,255,0],[0,120,240,3],0)
		screen.blit(bild_waffe, (0, 30))
		screen.blit(bild_herz, (0, 75))
		screen.blit(text_schuss,(100 - text_schuss.get_width() // 2, 45 - text_schuss.get_height() // 2))
		screen.blit(text_leben,(100 - text_leben.get_width() // 2, 95 - text_leben.get_height() // 2))
		screen.blit(text_uhrzeit,(220 - text_uhrzeit.get_width() // 2, 25 - text_uhrzeit.get_height() // 2))
		pygame.display.update()

thread.start_new_thread(neu,())
