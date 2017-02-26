from display import Display
from hardware import *
import network_client
import pygame
import time

display = Display(pygame, 100, 100)
display.redraw()

client = network_client.NetworkClient('olel', [255, 0, 255], '10.0.1.96')
client.join_game()
client.get_gameinfo()

hardware = Hardware()
hardware.set_weapon_characteristics(player_id=client.player_id, damage=20, laser=1, laser_duration=10, vibrate_power=255,
                                    vibrate_duration=5, muzzle_flash_r=50, muzzle_flash_g=0, muzzle_flash_b=0,
                                    muzzle_flash_w=0, muzzle_flash_duration=5)

ammo = 100
health = 100

while 1:
    try:
        enable, player_id, damage = hardware.get_hitpoint_results(I2CAddresses.HITPOINT0)

        if enable:
            health -= damage
            display.set_health(health)
            client.hit(player_id, damage)

        time.sleep(0.05)

        if hardware.is_weapon_button_down(0) and ammo > 0:
            hardware.shoot_weapon()
            ammo -= 1
            display.set_ammo(ammo)

            time.sleep(0.2)

        display.redraw()

    except Exception as e:
        print e
        break

client.quit_game()
