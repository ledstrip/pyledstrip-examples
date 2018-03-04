#!/usr/bin/env python
# coding: utf-8

import argparse

from periodicx import periodicx
from pyledstrip import LedStrip


class Beschleuniger:

    def __init__(self, startposition, geschwindigkeit, r, g, b):
        self.pos = 0
        self.startposition = startposition
        self.geschwindigkeit = geschwindigkeit
        self.r = r
        self.g = g
        self.b = b

    def malen(self, strip: LedStrip):
        strip.add_rgb((self.pos + self.startposition) * self.geschwindigkeit, self.r, self.g, self.b)
        self.pos = self.pos + 1


class Disco:
    PERIOD = 0.05

    # count = 100
    # _last_on = False
    RoterBeschleuniger = Beschleuniger(0, 0.5, 1.0, 0.0, 0.0)
    GruenerBeschleuniger = Beschleuniger(0, 1, 0.0, 1.0, 0.0)
    BlauerBeschleuniger = Beschleuniger(0, -1.5, 0.0, 0.0, 1.0)
    GelberBeschleuniger = Beschleuniger(0, 2, 0.5, 0.5, 0.0)
    TuerkisBeschleuniger = Beschleuniger(0, 2.5, 0.0, 0.5, 0.5)



    meineBeschleuniger = [RoterBeschleuniger,
                          GruenerBeschleuniger,
                          BlauerBeschleuniger,
                          GelberBeschleuniger,
                          TuerkisBeschleuniger,
                          Beschleuniger(150, 0.5, 1.0, 0.0, 0.0),
                          Beschleuniger(150, 1, 0.0, 1.0, 0.0),
                          Beschleuniger(150, -1.5, 0.0, 0.0, 1.0),
                          Beschleuniger(150, 2, 0.5, 0.5, 0.0),
                          Beschleuniger(150, 2.5, 0.0, 0.5, 0.5)]

    def update(self, strip: LedStrip):
        strip.clear()

        for einBeschleuniger in self.meineBeschleuniger:
            einBeschleuniger.malen(strip)

        strip.transmit()


def main(args):
    strip = LedStrip(args=args, loop=True)
    periodicx(Disco().update, Disco.PERIOD, strip)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
    LedStrip.add_arguments(parser)
    x = parser.parse_args()
    main(x)
