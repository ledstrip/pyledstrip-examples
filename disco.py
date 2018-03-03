#!/usr/bin/env python
# coding: utf-8

import argparse
import random

from periodicx import periodicx
from pyledstrip import LedStrip


class Disco:
    PERIOD = 0.05
    count = 100
    _last_on = False

    def update(self, strip):
        if self._last_on:
            strip.clear()
            hue = random.uniform(0.0, 1.0)
            for i in range(self.count):
                strip.set_hsv(int(random.random() * strip.led_count), hue, 1.0, 1.0)
            strip.transmit()
        else:
            strip.off()

        self._last_on = not self._last_on


def main(args):
    strip = LedStrip(args=args)
    periodicx(Disco().update, Disco.PERIOD, strip)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
    LedStrip.add_arguments(parser)
    main(parser.parse_args())
