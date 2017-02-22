# -*- coding:utf-8 -*-
import pygame
import logging

#
# Pygame-basierte Simulation der Hardware.py für die Entwicklung einer Lasertagwaffel ohne die eigentliche Hardware zu
# haben

# Autoren:
#   OleL

# TODO: Sowohl in hardware.py als auch in hardware_sim.py Methodennamen anpassen!

class i2cAddresses(object):
    BROADCAST = 0x00
    WEAPON = 0x03
    HITPOINT_WEAPON = 0x04
    HITPOINT0 = 0x04
    HITPOINT1 = 0x05
    HITPOINT2 = 0x06
    HITPOINT3 = 0x07
    HITPOINT4 = 0x08


class Hitpoint(object):

    def __init__(self):

        # Getroffen
        self.got_hit = False
        self.hit_by = 0
        self.hit_damage = 0

        # Led
        self.led_r = 0
        self.led_g = 0
        self.led_b = 0


class Hardware(object):

    def __init__(self):

        # Pügame
        screen = pygame.display.set_mode((1280, 720))
        screen.fill((255, 255, 255))
        pygame.display.flip()

        # Knöppe
        self.button_states = [0, 0, 0]  # 0: Trigger, 1: ???, 2: ???  TODO: WTF SIND 1 & 2

        # Getroffen
        self.got_hit = False
        self.hit_by = 0
        self.hit_damage = 0

        # Sensoren
        self.vbat = 65535  # Sollte 100% sein
        self.ldr = 21958  # Zufall... TODO: Wird dieser Sensor genutzt?

        # Eigenschaften (Waffe/Spieler)
        self.playerid = 0
        self.muzzle_flash_duration = 0
        self.laser_duration = 0
        self.vibrate_duration = 0
        self.weapon_damage = 0

        # Laser
        self.laser = 0

        # Vibrationsmotor
        self.vibrate_power = 0

        # RGBW Led
        self.muzzle_flash_r = 0  # \
        self.muzzle_flash_g = 0  # | Farbe beim schießen shoot
        self.muzzle_flash_b = 0  # |
        self.muzzle_flash_w = 0  # /
        self.led_r = 0  # \
        self.led_g = 0  # | Farbe im aktuellen Zustand
        self.led_b = 0  # |
        self.led_w = 0  # /

        # Hitpoints
            # Vier mal None um i2c Adressen zu behalten (Offset) am Anfang
            # Vier mal None um (bisher) nicht vorhandene Hardware zu representieren
        self.hitpoints = [None, None, None, None, Hitpoint(), None, None, None, None]

    def isWeaponButtonDown(self, button):
        return self.button_states[button]

    def getWeaponHitResults(self):
        return self.got_hit, self.hit_by, self.hit_damage

    def getWeaponVBat(self):
        return self.vbat % (2 ** 16)

    def getWeaponLDR(self):
        return self.ldr % (2 ** 16)

    def setWeaponCharacteristics(self, playerid, damage, laser, laser_duration, vibrate_power, vibrate_duration,
                                 muzzle_flash_r, muzzle_flash_g, muzzle_flash_b, muzzle_flash_w,
                                 muzzle_flash_duration):
        print(
            "playerid {0}; damage {1}; laser {2}; laser_duration {3}; vibrate_power {4}; vibrate_duration {5}; muzzle_flash_r {6}; muzzle_flash_b {7}; muzzle_flash_w {8}, muzzle_flash_duration {9}".format(
                playerid, damage, laser, laser_duration, vibrate_power, vibrate_duration, muzzle_flash_r,
                muzzle_flash_g,
                muzzle_flash_b, muzzle_flash_w, muzzle_flash_duration))

        self.playerid = playerid
        self.weapon_damage = damage
        self.laser = laser
        self.laser_duration = laser_duration
        self.vibrate_power = vibrate_power
        self.vibrate_duration = vibrate_duration
        self.muzzle_flash_r = muzzle_flash_r
        self.muzzle_flash_g = muzzle_flash_g
        self.muzzle_flash_b = muzzle_flash_b
        self.muzzle_flash_w = muzzle_flash_w
        self.muzzle_flash_duration = muzzle_flash_duration

    def shootWeapon(self):
        pass

    def setWeaponLED(self, R, G, B, W):
        self.led_r = R
        self.led_g = G
        self.led_b = B
        self.led_w = W

    def setWeaponLasers(self, laser):
        pass

    def getHitpointResults(self, hitpoint_address):
        return self.hitpoints[hitpoint_address].got_hit,\
               self.hitpoints[hitpoint_address].hit_by,\
               self.hitpoints[hitpoint_address].hit_damage

    def setHitpointLED(self, hitpoint_address, R, G, B):
        self.hitpoints[hitpoint_address].led_r = R
        self.hitpoints[hitpoint_address].led_g = G
        self.hitpoints[hitpoint_address].led_b = B


if __name__ == '__main__':
    import time

    hardware = Hardware()

    enable, playerid, damage = hardware.getWeaponHitResults()
    print("Waffe Hit Front enable: " + str(enable))
    print("Waffe Hit Front playerid: " + str(playerid))
    print("Waffe Hit Front damage: " + str(damage))

    enable, playerid, damage = hardware.getHitpointResults(i2cAddresses.HITPOINT_WEAPON)
    print("Waffe Hit Top enable: " + str(enable))
    print("Waffe Hit Top playerid: " + str(playerid))
    print("Waffe Hit Top damage: " + str(damage))

    print("Waffe Shoot: playerid=42, damage=123")
    # dauer in 0.1s
    hardware.setWeaponCharacteristics(playerid=42, damage=123, laser=1, laser_duration=10, vibrate_power=0,
                                      vibrate_duration=0, muzzle_flash_r=5, muzzle_flash_g=0, muzzle_flash_b=0,
                                      muzzle_flash_w=0, muzzle_flash_duration=25)

    hardware.shootWeapon()
    time.sleep(0.5)

    print("Waffe Button 0: " + str(hardware.isWeaponButtonDown(0)))
    print("Waffe Button 1: " + str(hardware.isWeaponButtonDown(1)))
    print("Waffe Button 2: " + str(hardware.isWeaponButtonDown(2)))

    enable, playerid, damage = hardware.getWeaponHitResults()
    print("Waffe Hit Front enable: " + str(enable))
    print("Waffe Hit Front playerid: " + str(playerid))
    print("Waffe Hit Front damage: " + str(damage))

    enable, playerid, damage = hardware.getHitpointResults(i2cAddresses.HITPOINT_WEAPON)
    print("Waffe Hit Top enable: " + str(enable))
    print("Waffe Hit Top playerid: " + str(playerid))
    print("Waffe Hit Top damage: " + str(damage))

    print("V_Bat: " + str(hardware.getWeaponVBat()))

    print("V_LDR: " + str(hardware.getWeaponLDR()))
