#!/usr/bin/env python
# coding: utf-8

import argparse
import time

from periodicx import periodicx
from pyledstrip import LedStrip


class Mod:
	PERIOD = 1 / 60
	SEC_PER_STEP = 1.8
	POS_PER_STEP = 53
	HUE_PER_STEP = 0.2341

	def update(self, strip):
		for pos in range(strip.led_count):
			strip.set_hsv(
				pos,
				(int(time.time() / self.SEC_PER_STEP + pos / self.POS_PER_STEP) * self.HUE_PER_STEP) % 1.0,
				1.0,
				1.0
			)
		strip.transmit()


def main(args):
	strip = LedStrip(args=args)
	periodicx(Mod().update, Mod.PERIOD, strip)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
	LedStrip.add_arguments(parser)
	main(parser.parse_args())
