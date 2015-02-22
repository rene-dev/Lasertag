#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import logging
import glob
from os.path import basename, splitext
import time
import pygame

logger = logging.getLogger(__name__)

class Sounds:
	sounds = {}

	def __init__(self):
		pygame.mixer.pre_init(44100, -16, 1, 512)
		
		for filename in glob.glob('sounds/*.wav'):
			name = splitext(basename(filename))[0]
			sound = pygame.mixer.Sound(filename)
			logger.debug('Loaded sound "%s" file "%s" length %.2f' % (
				name,
				filename,
				sound.get_length())
			)
			self.sounds[name] = sound

	def play(self, name, pause=False):
		logger.debug('Playing sound "%s"' % name)
		self.sounds[name].play()
		if pause:
			time.sleep(self.sounds[name].get_length())

	def wait(self):
		while pygame.mixer.get_busy():
			pass


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	sounds = Sounds()
	for sound in sounds.sounds:
		sounds.play(sound)
		sounds.wait()
