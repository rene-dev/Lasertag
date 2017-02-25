#!/usr/bin/python

import smbus


class I2CAddresses(object):
    BROADCAST = 0x00
    WEAPON = 0x03
    HITPOINT_WEAPON = 0x04
    HITPOINT0 = 0x04
    HITPOINT1 = 0x05
    HITPOINT2 = 0x06
    HITPOINT3 = 0x07
    HITPOINT4 = 0x08


class WeaponRegisters(object):
    LED_R = 0  # OUTPUT, Front-RGBW-LED: [0, 255]
    LED_G = 1  # OUTPUT, Front-RGBW-LED: [0, 255]
    LED_B = 2  # OUTPUT, Front-RGBW-LED: [0, 255]
    LED_W = 3  # OUTPUT, Front-RGBW-LED: [0, 255]
    LASER = 4  # OUTPUT, Laser (Platinenbeschriftung "Laser 2"): [0, 1]
    VIBRATION = 7  # OUTPUT, Vibrationsmotor (Platinenbeschriftung "Laser 1"): [0, 255] VORSICHT!
    BUTTON0 = 10  # INPUT,  Button
    BUTTON1 = 11  # INPUT,  Button
    BUTTON2 = 12  # INPUT,  Button
    SHOOT_ENABLED = 20  # OUTPUT, Fur Schuss auf 1 setzen, setzt sich selbst zuruck: [0, 1]
    SHOOT_PLAYERID = 21  # OUTPUT, Wird bei Schuss per IR gesendet: [0, 255]
    SHOOT_DAMAGE = 22  # OUTPUT, Wird bei Schuss per IR gesendet: [0, 255]
    SHOOT_LASER = 23  # OUTPUT, Laser an bei Schuss: [0, 1]
    SHOOT_LASER_DURATION = 24  # OUTPUT, Laser wie lange an bei Schuss: [0, 255] Einheit??
    SHOOT_VIBRATE_POWER = 25  # OUTPUT, Vibrationsmotor wie stark an bei Schuss, 0 == garnicht: [0, 255] VORSICHT!
    SHOOT_VIBRATE_DURATION = 26  # OUTPUT, Vibrationsmotor wie lange an bei Schuss: [0, 255] Einheit??
    SHOOT_MUZZLE_FLASH_R = 27  # OUTPUT, Front-RGBW-LED Helligkeit bei Schuss: [0, 255]
    SHOOT_MUZZLE_FLASH_G = 28  # OUTPUT, Front-RGBW-LED Helligkeit bei Schuss: [0, 255]
    SHOOT_MUZZLE_FLASH_B = 29  # OUTPUT, Front-RGBW-LED Helligkeit bei Schuss: [0, 255]
    SHOOT_MUZZLE_FLASH_W = 30  # OUTPUT, Front-RGBW-LED Helligkeit bei Schuss: [0, 255]
    SHOOT_MUZZLE_FLASH_DURATION = 31  # OUTPUT, Front-RGBW-LED wie lange an bei Schuss: [0, 255] Einheit??
    HIT_ENABLE = 40  # INPUT,  1 wenn getroffen, setzt sich bei Auslesen auf 0 zuruck: [0, 1]
    HIT_PLAYERID = 41  # INPUT,  PlayerID des Schutzen: [0, 255]
    HIT_DMG = 42  # INPUT,  Angerichteter Schaden: [0, 255]
    V_BAT_L = 50  # INPUT,  Akkustand 16-Bit Wert zusammen mit V_BAT_R: [0, 255]
    V_BAT_R = 51  # INPUT,  Akkustand 16-Bit Wert zusammen mit V_BAT_L: [0, 255]
    LDR_L = 52  # INPUT,  Helligkeit 16-Bit Wert zusammen mit LDR_R: [0, 255]
    LDR_R = 53  # INPUT,  Helligkeit 16-Bit Wert zusammen mit LDR_L: [0, 255]


class HitpointRegisters(object):
    VIBRATION = 7  # OUTPUT, Vibrationsmotor: [0, 255] Noch nicht in Hardware vorhanden.
    HIT_ENABLE = 30  # INPUT,  1 wenn getroffen, setzt sich bei Auslesen auf 0 zuruck: [0, 1]
    HIT_PLAYERID = 31  # INPUT,  PlayerID des Schutzen: [0, 255]
    HIT_DMG = 32  # INPUT,  Angerichteter Schaden: [0, 255]
    LED_R = 50  # OUTPUT, 4 RGB-LEDs: [0, 255]
    LED_G = 51  # OUTPUT, 4 RGB-LEDs: [0, 255]
    LED_B = 52  # OUTPUT, 4 RGB-LEDs: [0, 255]


class Hardware(object):
    def __init__(self):
        self.bus = None

        self.connect()

        self.set_weapon_lasers(laser=0)
        self.set_weapon_led(0, 0, 0, 0)
        self.set_hitpoint_led(I2CAddresses.HITPOINT_WEAPON, 0, 0, 0)


    # ----------------- low level -----------------
    def connect(self):
        try:
            self.bus = smbus.SMBus(0)  # alte PIs
        except:
            self.bus = smbus.SMBus(1)  # neuere PIs

    def disconnect(self):
        del self.bus

    def reconnect(self):
        self.disconnect()
        self.connect()

    def read(self, i2c_adr, register):
        while True:
            try:
                return self.bus.read_byte_data(i2c_adr, register)
            except IOError:
                self.reconnect()

    def write(self, i2c_adr, register, data):
        while True:
            try:
                self.bus.write_byte_data(i2c_adr, register, data)
                break
            except TypeError:
                print "Exception 'TypeError' in def write:", i2c_adr, register, data  # Debug informations
            except IOError:
                self.reconnect()

    # ----------------- Lasermodul -----------------

    def is_weapon_button_down(self, button):
        return self.read(I2CAddresses.WEAPON, WeaponRegisters.BUTTON0 + button) == 1

    def get_weapon_hit_results(self):
        player_id = self.read(I2CAddresses.WEAPON, WeaponRegisters.HIT_PLAYERID)
        damage = self.read(I2CAddresses.WEAPON, WeaponRegisters.HIT_DMG)
        enable = self.read(I2CAddresses.WEAPON, WeaponRegisters.HIT_ENABLE) != 0
        return enable, player_id, damage

    def get_weapon_vbat(self):
        left = self.read(I2CAddresses.WEAPON, WeaponRegisters.V_BAT_L)
        right = self.read(I2CAddresses.WEAPON, WeaponRegisters.V_BAT_R)
        return left * 256 + right   # TODO: Stimmt das so??

    def get_weapon_brightness(self):
        left = self.read(I2CAddresses.WEAPON, WeaponRegisters.LDR_L)
        right = self.read(I2CAddresses.WEAPON, WeaponRegisters.LDR_R)
        return left * 256 + right   # TODO: Stimmt das so??

    def set_weapon_characteristics(self, player_id, damage, laser, laser_duration, vibrate_power, vibrate_duration,
                                   muzzle_flash_r, muzzle_flash_g, muzzle_flash_b, muzzle_flash_w, muzzle_flash_duration):

        print "Weapon characteristics:"
        print "\tplayer_id:", player_id
        print "\tdamage:", damage
        print "\tlaser:", laser
        print "\tlaser_duration:", laser_duration
        print "\tvibrate_power:", vibrate_duration
        print "\tvibrate_duration:", vibrate_duration
        print "\tmuzzle_flash (r, g, b, w):", muzzle_flash_r, muzzle_flash_g, muzzle_flash_b, muzzle_flash_w
        print "\tmuzzle_flash_duration:", muzzle_flash_duration

        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_PLAYERID, playerid)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_DAMAGE, damage)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_LASER, laser)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_LASER_DURATION, laser_duration)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_VIBRATE_POWER, vibrate_power)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_VIBRATE_DURATION, vibrate_duration)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_MUZZLE_FLASH_R, muzzle_flash_r)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_MUZZLE_FLASH_G, muzzle_flash_g)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_MUZZLE_FLASH_B, muzzle_flash_b)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_MUZZLE_FLASH_W, muzzle_flash_w)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_MUZZLE_FLASH_DURATION, muzzle_flash_duration)

    def shoot_weapon(self):
        self.write(I2CAddresses.WEAPON, WeaponRegisters.SHOOT_ENABLED, 1)

    def set_weapon_led(self, r, g, b, w):
        self.write(I2CAddresses.WEAPON, WeaponRegisters.LED_R, r)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.LED_G, g)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.LED_B, b)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.LED_W, w)

    def set_weapon_lasers(self, laser):
        self.write(I2CAddresses.WEAPON, WeaponRegisters.LASER, laser)

    def vibrate(self, duration, power):
        self.write(I2CAddresses.WEAPON, WeaponRegisters.VIBRATION, power)
        time.sleep(duration)
        self.write(I2CAddresses.WEAPON, WeaponRegisters.VIBRATION, 0)

    # ----------------- Trefferzonenmodul -----------------

    def get_hitpoint_results(self, hitpoint_address):
        player_id = self.read(hitpoint_address, HitpointRegisters.HIT_PLAYERID)
        damage = self.read(hitpoint_address, HitpointRegisters.HIT_DMG)
        enable = self.read(hitpoint_address, HitpointRegisters.HIT_ENABLE) != 0
        return enable, player_id, damage

    def set_hitpoint_led(self, hitpoint_address, r, g, b):
        self.write(hitpoint_address, HitpointRegisters.LED_R, r)
        self.write(hitpoint_address, HitpointRegisters.LED_G, g)
        self.write(hitpoint_address, HitpointRegisters.LED_B, b)


if __name__ == '__main__':
    import time

    hardware = Hardware()

    hardware.set_hitpoint_led(I2CAddresses.HITPOINT_WEAPON, 127, 127, 127)
    time.sleep(0.1)
    hardware.set_hitpoint_led(I2CAddresses.HITPOINT_WEAPON, 0, 0, 0)

    hardware.vibrate(0.1, 100)

    enable, playerid, damage = hardware.get_weapon_hit_results()
    print("Waffe Hit Front enable: " + str(enable))
    print("Waffe Hit Front playerid: " + str(playerid))
    print("Waffe Hit Front damage: " + str(damage))

    enable, playerid, damage = hardware.get_hitpoint_results(I2CAddresses.HITPOINT_WEAPON)
    print("Waffe Hit Top enable: " + str(enable))
    print("Waffe Hit Top playerid: " + str(playerid))
    print("Waffe Hit Top damage: " + str(damage))

    print("Waffe Shoot: playerid=42, damage=123")

    hardware.set_weapon_characteristics(player_id=42, damage=123, laser=1, laser_duration=10, vibrate_power=0,
                                        vibrate_duration=0, muzzle_flash_r=5, muzzle_flash_g=0, muzzle_flash_b=0,
                                        muzzle_flash_w=0, muzzle_flash_duration=25)

    hardware.shoot_weapon()
    time.sleep(0.5)

    print"Waffe Button 0:", hardware.is_weapon_button_down(0)
    print"Waffe Button 1:", hardware.is_weapon_button_down(1)
    print"Waffe Button 2:", hardware.is_weapon_button_down(2)

    enable, player_id, damage = hardware.get_weapon_hit_results()
    print "Waffe Hit Front enable:", enable
    print "Waffe Hit Front playerid:", playerid
    print "Waffe Hit Front damage:", damage

    enable, player_id, damage = hardware.get_hitpoint_results(I2CAddresses.HITPOINT_WEAPON)
    print "Waffe Hit Top enable:", enable
    print "Waffe Hit Top playerid:", player_id
    print "Waffe Hit Top damage:", damage

    print "V_Bat:", hardware.get_weapon_vbat()

    print "V_LDR:", hardware.get_weapon_brightness()
