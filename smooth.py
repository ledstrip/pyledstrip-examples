#!/usr/bin/env python
# coding: utf-8

import argparse
import time

from periodicx import periodicx
from pyledstrip import LedStrip


class Smooth:
    PERIOD = 1 / 60

    def __init__(self, strip):
        self.strip = strip
        self.brightness = 0.3

    def set(self, pos: float):
        p1 = int(pos)
        p2 = p1 + 1
        f1 = self.brightness * pow(min(abs(pos - p2) * 2, 1.0), 2)
        f2 = self.brightness * pow(min(abs(pos - p1) * 2, 1.0), 2)
        self.strip.set_rgb(p1, f1, f1, f1)
        self.strip.set_rgb(p2, f2, f2, f2)

    def update(self):
        self.strip.clear()
        self.set(time.time() * 5)
        self.strip.transmit()


def main(args):
    strip = LedStrip(args=args, loop=True)
    periodicx(Smooth(strip).update, Smooth.PERIOD)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
    LedStrip.add_arguments(parser)
    main(parser.parse_args())
