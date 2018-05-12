#!/usr/bin/env python
# coding: utf-8

import argparse
import random

from periodicx import periodicx
from pyledstrip import LedStrip

_INDEX_POS = 0
_INDEX_VELO = 1
_INDEX_HUE = 2
_INDEX_SAT = 3

class Walker:
    VELO_MAX = 20 # LED / sec
    PERIOD = 1 / 60

    _VELO_MAX = VELO_MAX * PERIOD

    def __init__(self, strip):
        self.strip = strip
        self.walkers = [[pos, random.uniform(-self._VELO_MAX, self._VELO_MAX), random.uniform(0, 1), random.uniform(0, 1)] for pos in range(0, self.strip.led_count, 5)]

    def update(self):
        self.strip.clear()
        for i in range(len(self.walkers)):
            # update position
            self.walkers[i][_INDEX_POS] = (self.walkers[i][_INDEX_POS] + self.walkers[i][_INDEX_VELO]) % self.strip.led_count
            # update velocity
            self.walkers[i][_INDEX_VELO] = max(min(self.walkers[i][_INDEX_VELO] + random.uniform(-0.01, 0.01), self._VELO_MAX), -self._VELO_MAX)
            # change hue & saturation
            self.walkers[i][_INDEX_HUE] = self.walkers[i][_INDEX_HUE] + random.uniform(-0.01, 0.01) % 1
            self.walkers[i][_INDEX_SAT] = max(min(self.walkers[i][_INDEX_SAT] + random.uniform(-0.005, 0.01), 1), 0)
            # add walker to strip
            self.strip.add_hsv(self.walkers[i][_INDEX_POS], self.walkers[i][_INDEX_HUE], self.walkers[i][_INDEX_SAT], 1)
        self.strip.transmit()


def main(args):
    strip = LedStrip(args=args, loop=True)
    periodicx(Walker(strip).update, Walker.PERIOD)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
    LedStrip.add_arguments(parser)
    main(parser.parse_args())
