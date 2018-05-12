#!/usr/bin/env python
# coding: utf-8

import argparse

from pyledstrip import LedStrip


def main(args):
    strip = LedStrip(args=args, loop=True)
    strip.clear()

    brightness = 1

    if args.hsv is True:
        # --hsv
        for i in range(strip.led_count):
            strip.set_hsv(i, i/strip.led_count, 1, brightness)
    else:
        # --blank
        for i in range(strip.led_count):
            strip.set_hsv(i, 1, 0, brightness)

    strip.transmit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
    LedStrip.add_arguments(parser)

    parser.add_argument('--blank', action='store_true', help='Set all LEDs white')
    parser.add_argument('--hsv', action='store_true', help='HSV sweep. Set all LEDs hue based on their position on the strip. (default)')

    main(parser.parse_args())
