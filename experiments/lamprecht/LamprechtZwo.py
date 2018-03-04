#!/usr/bin/env python
# coding: utf-8

import argparse
import random

from periodicx import periodicx
from pyledstrip import LedStrip

PERIOD = 0.05


class Debris:
    def __init__(self, pos, v, ch, cs, cv):
        self.pos = pos
        self.v = v
        self.ch = ch
        self.cs = cs
        self.cv = cv
        self.age = 0

    def move(self, t):
        self.age += t
        self.cv *= 0.9
        self.pos += self.v * t

        if self.age > 3:
            return []
        else:
            return [self]

    def paint(self, strip: LedStrip):
        strip.add_hsv(self.pos,
                      0.66,  # self.ch,
                      self.cs, self.cv)


class Rocket:
    def __init__(self, pos, v, ch, cs, cv):
        self.pos = pos
        self.v = v
        self.ch = ch
        self.cs = cs
        self.cv = cv
        self.age = 0

    def move(self, t):
        self.age += t
        self.pos += self.v * t

        if self.age > 3:
            debris = []
            for i in range(3):
                item = Debris(self.pos, 10 * random.uniform(-1, 1), random.uniform(0, 1), 1, 1)
                debris.append(item)
            return debris
        else:
            return [self]

    def paint(self, strip: LedStrip):
        strip.add_hsv(self.pos,
                      0.33,  # self.ch,
                      self.cs, self.cv)


class Launcher:
    def __init__(self, pos, ch, cs, cv):
        self.pos = pos
        self.ch = ch
        self.cs = cs
        self.cv = cv
        self.age = 0
        self.freq = 3 * random.uniform(0.5, 1)

    def move(self, t):
        self.age += t

        if self.age > self.freq:
            self.age -= self.freq
            rocket = Rocket(
                self.pos,
                10 * random.uniform(0.5, 1),
                random.uniform(0, 1),
                1,
                1
            )
            return [self, rocket]
        else:
            return [self]

    def paint(self, strip: LedStrip):
        strip.add_hsv(self.pos,
                      0.00,  # self.ch,
                      self.cs, self.cv)


class World:

    def __init__(self, strip: LedStrip):
        worldsize = strip.led_count

        self.lauchners = []
        for i in range(3):
            self.lauchners.append(
                Launcher(
                    random.uniform(0, worldsize),
                    0,
                    1,
                    1
                )
            )

    def update(self, strip: LedStrip):
        strip.clear()

        newStuff = []
        for rocket in self.lauchners:
            results = rocket.move(PERIOD)  # tickrate is perfect
            newStuff += results

        self.lauchners = newStuff

        for rocket in self.lauchners:
            rocket.paint(strip)

        strip.transmit()


def main(args):
    strip = LedStrip(args=args, loop=True)
    periodicx(World(strip).update, PERIOD, strip)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
    LedStrip.add_arguments(parser)
    main(parser.parse_args())
