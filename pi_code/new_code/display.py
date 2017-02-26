import time
import pygame


class Display:
    def __init__(self, pygame_instance, health, ammo):
        self.pygame = pygame_instance
        self.screen = self.pygame.display.set_mode((240, 320))
        self.pygame.mouse.set_visible(False)
        self.pygame.font.init()
        self.font1 = self.pygame.font.SysFont("monosans", 72)
        self.font2 = self.pygame.font.SysFont("monosans", 25)
        self.sprite_weapon = self.pygame.image.load("res/images/ammo.png")
        self.sprite_heart = self.pygame.image.load("res/images/heart.png")

        self.text_ammo = None
        self.text_health = None
        self.text_clock = None

        self.last_clock = ""
        self.set_health(health)
        self.set_ammo(ammo)

    def set_ammo(self, ammo):
        self.text_ammo = self.font1.render(str(ammo), True, (255, 0, 0))

    def set_health(self, health):
        self.text_health = self.font1.render(str(health), True, (255, 0, 0))

    def redraw(self):
        # update clock text
        current_clock = time.strftime("%H:%M:%S")
        if current_clock != self.last_clock:
            self.text_clock = self.font2.render(current_clock, True, (255, 0, 0))
            self.last_clock = current_clock

        # clear and redraw everything
        self.screen.fill((0, 0, 0))
        self.pygame.draw.rect(self.screen, (80, 80, 80), (0, 0, 240, 17), 0)
        self.pygame.draw.rect(self.screen, (127, 0, 0), (5, 5, 3, 10), 0)
        self.pygame.draw.rect(self.screen, (127, 0, 0), (10, 8, 3, 7), 0)
        self.pygame.draw.rect(self.screen, (127, 0, 0), (15, 12, 3, 3), 0)
        self.pygame.draw.rect(self.screen, (127, 0, 0), (0, 70, 240, 3), 0)
        self.pygame.draw.rect(self.screen, (127, 0, 0), (0, 120, 240, 3), 0)
        self.screen.blit(self.sprite_weapon, (0, 30))
        self.screen.blit(self.sprite_heart, (0, 75))
        self.screen.blit(self.text_ammo, (100 - self.text_ammo.get_width() // 2, 45 - self.text_ammo.get_height() // 2))
        self.screen.blit(self.text_health,
                         (100 - self.text_health.get_width() // 2, 95 - self.text_health.get_height() // 2))
        self.screen.blit(self.text_clock, (175, 0))
        self.pygame.display.flip()

if __name__ == "__main__":
    display = Display(pygame, 100, 100)

    while 1:
        display.redraw()
        time.sleep(0.75)

    while 1: pass