#!/usr/bin/env python
# coding: utf-8

import argparse
import math
import time

from periodicx import periodicx
from pyledstrip import LedStrip


class Boomerang:
	def __init__(self, a1, f1, p1, c1, a2, f2, p2, red, green, blue):
		self.a1 = a1
		self.f1 = f1
		self.p1 = p1
		self.c1 = c1
		self.a2 = a2
		self.f2 = f2
		self.p2 = p2
		self.red = red
		self.green = green
		self.blue = blue

	def update(self, strip):
		t = time.time()
		p = int(strip.led_count * (self.c1 + 0.5 + self.a1 * 0.5 * math.sin((t * self.f1 + self.p1) * 2 * math.pi)))
		s = int(self.a2 * strip.led_count * math.sin((t * self.f2 + self.p2) * 2 * math.pi))
		p1 = min(p - s, p + s)
		p2 = max(p - s, p + s)

		# Boomerang
		for i in range(p1, p2 + 1):
			strip.add_pixel_rgb(i, self.red, self.green, self.blue)

		# End points
		strip.add_pixel_rgb(p1 - 1, 1, 1, 0)
		strip.add_pixel_rgb(p2 + 1, 1, 1, 0)


class Boomerangs:
	PERIOD = 1 / 60

	def __init__(self):
		self.boomerangs = [
			Boomerang(0.7, 0.3, 0.1, 0, 0.1, 0.9, 0.2, 1, 0, 0),
			Boomerang(0.6, 0.33, 0.4, 0.1, 0.11, 0.91, 0.31, 0, 1, 0),
			Boomerang(0.8, 0.21, 0.6, -0.05, 0.06, 0.82, 0.78, 0, 0, 1),
		]

	def update(self, strip):
		strip.clear()
		for boomerang in self.boomerangs:
			boomerang.update(strip)
		strip.transmit()


def main(args):
	strip = LedStrip(args=args)
	periodicx(Boomerangs().update, Boomerangs.PERIOD, strip)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
	LedStrip.add_arguments(parser)
	main(parser.parse_args())
