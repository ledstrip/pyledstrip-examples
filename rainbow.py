#!/usr/bin/env python
# coding: utf-8

import argparse
import time

from periodicx import periodicx
from pyledstrip import LedStrip


class Rainbow:
    PERIOD = 1 / 60

    @staticmethod
    def update(strip):
        strip.clear()
        for pos in range(0, strip.led_count, 10):
            strip.set_hsv(pos + time.time() * 10, ((pos * 10 + int(time.time() * 20)) / strip.led_count) % 1.0, 1.0,
                          1.0)
        strip.transmit()


def main(args):
    strip = LedStrip(args=args, loop=True)
    periodicx(Rainbow().update, Rainbow.PERIOD, strip)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
    LedStrip.add_arguments(parser)
    main(parser.parse_args())
