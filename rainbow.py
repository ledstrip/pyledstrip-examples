#!/usr/bin/env python3

# A slowly glowing rainbow. As it turns out HSV is not suitable to implement
# a rainbow on an RGB strip because leds have a different intensity. This
# picks some suitable color values that worked for the developer's strip
# and dampens the blue color rail. Tested with the default power_limit of
# 0.2.

import argparse
import collections

from periodicx import periodicx
from pyledstrip import LedStrip


Color = collections.namedtuple('Color', ['r', 'g', 'b'])

class Rainbow:
    PERIOD = 0.1

    BASE_COLORS = [
            Color(0.32, 0, 0.40), # dampened violet
            Color(0, 0, 1.0),     # blue
            Color(0, 1.0, 0),     # green
            Color(1.0, 0.75, 0),  # yellow
            Color(1.0, 0.25, 0),  # orange
            Color(1.0, 0, 0),     # red
    ]

    def __init__(self, strip: LedStrip):
        self.strip = strip
        self.rainbow = [Color(0.0, 0.0, 0.0)] * 450
        self.init_colors()
        self.i = 0
    
    def color(self, start: Color, end: Color, steps: int):
        """Interpolates the steps between start and end."""
        result = [start]
        r_delta = (end.r - start.r) / (steps - 1)
        g_delta = (end.g - start.g) / (steps - 1)
        b_delta = (end.b - start.b) / (steps - 1)
        for i in range(0, steps-2):
            result.append(Color(
                result[-1].r + r_delta,
                result[-1].g + g_delta,
                result[-1].b + b_delta,
            ))
        return result

    def init_colors(self):
        n = 0
        for k in range(0, 5):
            # Cycle through the base colors.
            for i in range(0, len(self.BASE_COLORS)):
                start = self.BASE_COLORS[i]
                end = self.BASE_COLORS[(i + 1) % len(self.BASE_COLORS)]
                for cols in self.color(start, end, 16):
                    self.rainbow[n] = cols
                    n += 1

    def update(self):
        self.strip.clear()
        if self.i >= 90:
           self.i = -1
        self.i += 1
        for j in range(self.i, 300 + self.i):
            cols = self.rainbow[j]
            self.strip.add_rgb(j - self.i, cols.r, cols.g, cols.b * cols.b)
        self.strip.transmit()
    

def main(args):
    strip = LedStrip(args=args, loop=True)
    periodicx(Rainbow(strip).update, Rainbow.PERIOD)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Rainbow implementation using pyledstrip.')
    LedStrip.add_arguments(parser)
    x = parser.parse_args()
    main(x)
