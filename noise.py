#!/usr/bin/env python
# coding: utf-8

import argparse
import random

from periodicx import periodicx
from pyledstrip import LedStrip


class Noise:
    PERIOD = 1.5

    @staticmethod
    def update(strip):
        strip.clear()
        for i in range(int(strip.led_count / 3)):
            strip.set_hsv(int(random.random() * strip.led_count), random.random(), 1.0, 1.0)
        strip.transmit()


def main(args):
    strip = LedStrip(args=args)
    periodicx(Noise().update, Noise.PERIOD, strip)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
    LedStrip.add_arguments(parser)
    main(parser.parse_args())
