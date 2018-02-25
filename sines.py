#!/usr/bin/env python
# coding: utf-8

import argparse
import math
import time

from periodicx import periodicx
from pyledstrip import LedStrip


class Sines:
	PERIOD = 1 / 60

	def update(self, strip):
		for i in range(strip.led_count):
			strip.set_pixel_rgb(
				i,
				0.5 + 0.5 * math.sin(float(time.time() + 0) / 2.5 + float(i + 0) / 200.0 + 0.0),
				0.5 * 0.5 * math.sin(float(time.time() + 7.5) / 1.75 + float(i + 100) / 200.0 + 1.3),
				0.5 * 0.5 * math.sin(float(time.time() + 25) / 3.25 + float(i + 200) / 200.0 + 2.1)
			)
		strip.transmit()


def main(args):
	strip = LedStrip(args=args)
	periodicx(Sines().update, Sines.PERIOD, strip)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
	LedStrip.add_arguments(parser)
	main(parser.parse_args())
